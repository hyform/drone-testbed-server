from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from django.views import generic
from repo.models import DesignTeam, Vehicle, Address, Customer, CustomerScenario, Warehouse, Scenario, Waypoint, Path, Plan, DataLog
from repo.models import VehicleDemo, ScenarioDemo, OpsPlanDemo, PlayDemo, PathCustomer
from repo.serializers import UserSerializer, TeamSerializer, VehicleSerializer, AddressSerializer, CustomerSerializer, WarehouseSerializer
from repo.serializers import ScenarioSerializer, WaypointSerializer, PathSerializer, PlanSerializer, DataLogSerializer
from repo.serializers import DLSerializer, VDSerializer, SDSerializer, OPDSerializer, PDSerializer, Plan2Serializer, PlanShortSerializer
from repo.serializers import MediationCountSerializer, MediationChatSerializer
from django.http import Http404
from exper.models import UserPosition, SessionTeam, GroupPosition, Session
from django.db.models import Q
from chat.messaging import new_vehicle_message, new_plan_message, new_scenario_message
from api.messaging import event_info_message
from api.models import SessionTimer
import time
from datetime import datetime, timedelta, timezone
from functools import reduce
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import hunspell
import numpy as np
from sklearn.decomposition import TruncatedSVD
from scipy.spatial.distance import pdist, squareform
import logging
from ai.agents.botmanager import BotManager

logger = logging.getLogger(__name__)

spellchecker = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
tokenizer = RegexpTokenizer(r'\w+')
porter = PorterStemmer()

class VehicleList(generics.ListCreateAPIView):
    """
    List all vehicle entries, or create a new vehicle entry.
    """
    # queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
            groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
            qs = Vehicle.objects.filter(group__in=groups, session=st.session)
        else:
            qs = Vehicle.objects.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
            gp = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)&Q(primary=True)).first()
            # self.request.data['group']=gp.group.id
            # self.request.data['session']=st.session.id
            # serializer.save(data=self.request.data)
            serializer.save(group=gp.group, session=st.session)
            tag = None
            data = self.request.data
            if 'tag' in data:
                tag = data['tag']
            new_vehicle_message(gp.group, st.session, tag)
        else:
            raise ValidationError('You are not in an active session')


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a vehicle entry.
    """
    # queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        return Vehicle.objects.filter(group__in=groups, session=st.session)


class ScenarioDetail(APIView):
    """
    Retreive or Create a scenario entry.
    """
    parser_classes = [JSONParser]

    def get_object(self, request, ver):
        # the default version of -1 means return the last version
        # if not scenario exists for this session/group combo - create a new one
        user = request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st==None:
            return None
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure))
        scenarios = Scenario.objects.filter(Q(group__in=groups.values('group'))&Q(session=st.session))
        if scenarios.exists():
            # there is at least one scenario already
            if ver==-1:
                # the default is to return the last one
                return scenarios.order_by('version').last()
            else:
                return scenarios.get(version=ver)
        else:
            # this will make a new scenario
            warehouse = Warehouse.objects.filter(Q(group__in=groups.values('group'))&Q(session=st.session)).first()
            group = groups.filter(primary=True).first()
            scenario = Scenario.objects.create(tag='Initial Scenario', warehouse=warehouse, group=group.group, session = st.session)
            # also need to select all of the customer's in this market
            market = st.session.market
            customers = Customer.objects.filter(market=market)
            for customer in customers:
                # this may be a little slow - keep an eye on it
                # may want to create a lsit of objects and then use bulk_create
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=True)
            return scenario


    def get(self, request, ver=-1):
        scenario = self.get_object(request, ver)
        serializer = ScenarioSerializer(scenario)
        return Response(serializer.data)


    def put(self, request, ver=-1):
        # grab the last version of the scenario
        scenario = self.get_object(request, ver)
        # get all of the customers
        customers = Customer.objects.filter(market=scenario.session.market)
        # increment version number
        tag = request.data.get('tag', scenario.tag)
        scenario = Scenario.objects.create(tag=tag, warehouse=scenario.warehouse, group=scenario.group, session=scenario.session, version=scenario.version+1)
        clist = request.data.get('customers', [])
        for customer in customers:
            if customer.id in clist:
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=True)
            else:
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=False)
        new_scenario_message(scenario.group, scenario.session)
        return Response(status=status.HTTP_201_CREATED)


class PlanList(generics.ListCreateAPIView):
    """
    List all plan entries or create a new plan entry
    """
    # queryset = Plan.objects.all()
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session))
        logger.debug("time to get plans - %s secs" % (time.time() - start_time))
        return plans
        # return Plan.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        gp = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)&Q(primary=True)).first()
        # first step is to create a plan object
        data = self.request.data
        scenario = Scenario.objects.get(id=data.get('scenario'))
        plan = Plan.objects.create(tag=data.get('tag'), scenario=scenario, group=gp.group, session=st.session)
        # next is to create the path objects
        paths = data.get('paths')
        for p in paths:
            vehicle = Vehicle.objects.get(id=p.get('vehicle'))
            warehouse = Warehouse.objects.get(id=p.get('warehouse'))
            path = Path.objects.create(plan=plan, vehicle=vehicle, warehouse=warehouse, leavetime=p.get('leavetime',0.0),
                returntime=p.get('returntime',0.0))
            # next we need to define the customers in the path
            customers = p.get('customers')
            stop=1
            for c in customers:
                customer = Customer.objects.get(id=c)
                PathCustomer.objects.create(path=path, customer=customer, stop=stop)
                stop=stop+1
        new_plan_message(gp.group, st.session, plan.tag)
        # return Response(status=status.HTTP_201_CREATED)

    serializer_class = PlanSerializer

class Plan2List(generics.ListAPIView):
    """
    List all plan entries or create a new plan entry
    """
    # queryset = Plan.objects.all()
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session))
        logger.debug("time to get plans - %s secs" % (time.time() - start_time))
        return plans
        # return Plan.objects.all()

    serializer_class = Plan2Serializer
class PlanShortList(generics.ListAPIView):
    """
    List all plan entries for the session - short version
    """
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session)).order_by('id')
        logger.debug("time to get plans - %s secs" % (time.time() - start_time))
        return plans

    serializer_class = PlanShortSerializer

class PlanDetail(generics.RetrieveAPIView):
    """
    Retrieve a plan entry.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class DataLogList(generics.CreateAPIView):
    """
    Create a new DataLog Entry
    """
    # queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            channel = 'm_' + str(st.session.id)
            log = str(serializer)
            action_val = serializer.validated_data.get('action')
            logger.debug("perform_create: action = " + str(action_val))
            if action_val:
                logger.debug("perform_create: before if 'Open' in action_val:")
                if "Open" in action_val:
                    logger.debug("perform_create: "Open" in action_val == true")
                    BotManager.set_metrics_From_open(st.session.id, user.username, action_val)
                logger.debug("perform_create: after if 'Open' in action_val:")
                values = action_val.split(';')
                length = len(values)
                if length > 0:
                    # should be more specific, but client source strings aren't consistent
                    first = action_val
                    action = None
                    ITERATE_ON_DESIGN = "Iterate on Design"
                    EVALUATE_SUBMIT_DESIGN = "Evaluate/Submit Design"
                    RUN_DESIGN_AGENT = "Run Design Agent"
                    ITERATING_ON_PATH = "Iterating on path"
                    RUNNING_AI = "Running AI"
                    SUBMIT_PLAN = "Submit Plan"

                    # temporary checks until we can send better messages from the client
                    if "ToggleCWMotor" in first:
                        action = "Iterate on Design"
                    elif "ScaleUp" in first:
                        action = "Iterate on Design"
                    elif "AssemblyHandle" in first:
                        action = "Iterate on Design"
                    elif "Evaluate" in first:
                        action = "Evaluate/Submit Design"
                    elif "AssemblyChange" in first:
                        action = "Iterate on Design"
                    elif "SubmittingToDB" in first:
                        action = "Evaluate/Submit Design"
                    elif "ToggleFoil" in first:
                        action = "Iterate on Design"
                    elif "ToggleStructure" in first:
                        action = "Iterate on Design"
                    elif "CapacityInput" in first:
                        action = "Iterate on Design"
                    elif "SelectedAIDesign" in first:
                        action = "Run Design Agent"
                    elif "HotKeyComponentToMotorCCW" in first:
                        action = "Iterate on Design"
                    elif "HotKeyComponentToMotorCW" in first:
                        action = "Iterate on Design"
                    elif "ResetView" in first:
                        action = "Iterate on Design"
                    elif "HotKeyComponentToFoil" in first:
                        action = "Iterate on Design"
                    elif "HotKeyComponentToStructure'" in first:
                        action = "Iterate on Design"
                    elif "ManualPathAdded" in first:
                        action = "Iterating on path"
                    elif "ManualPathRemove" in first:
                        action = "Iterating on path"
                    elif "OrthogonalCamera" in first:
                        action = "Iterating on path"
                    elif "PathMetrics" in first:
                        action = "Iterating on path"
                    elif "PerspectiveCamera" in first:
                        action = "Iterating on path"
                    elif "RemoveAllPaths" in first:
                        action = "Iterating on path"
                    elif "ResetView" in first:
                        action = "Iterating on path"
                    elif "RunPathAgent" in first:
                        action = "Running AI"
                    elif "SelectPath" in first:
                        action = "Iterating on path"
                    elif "SubmitPlanToDB" in first:
                        action = "Submit Plan"
                    elif "SubmitScenario" in first:
                        action = "Submit Plan"
                    elif "ToggleInfoPanel" in first:
                        action = "Iterating on path"
                    elif "ToggleWeightIcons" in first:
                        action = "Iterating on path"
                    elif "VehicleDuplicated" in first:
                        action = "Iterating on path"
                    elif "VehiclePathRemoved" in first:
                        action = "Iterating on path"
                    elif "VehicleToggle'" in first:
                        action = "Iterating on path"

                    if action:
                        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
                        if up:
                            running_timer = SessionTimer.objects.filter(session=st.session).filter(timer_type=SessionTimer.RUNNING_START).first()
                            elapsed_seconds = -1
                            if running_timer:
                                current_time = datetime.now(timezone.utc)
                                running_timestamp = running_timer.timestamp
                                if running_timestamp:
                                    time_difference = current_time - running_timestamp
                                    elapsed_seconds = round(time_difference.total_seconds())
                            else:
                                elapsed_seconds = 0

                            event_info_message(channel, up.position.name, action, elapsed_seconds)

            serializer.save(user=user, session=st.session, type='client')
        else:
            raise ValidationError('You are not in an active session')

class MediationCountView(APIView):
    """
    Return count data for Mediation
    """

    def get(self, request, session_id, section_id=0, format=None):
        data = self.get_data(session_id, section_id)
        mediationCount = MediationCountSerializer(data)
        return Response(mediationCount.data)

    def get_data(self, session_id, section_id ):
        data ={"session_id" : session_id}
        session = Session.objects.get(id=data["session_id"])
        start_time = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()

        # Calculate the start and end times for the desired interval
        starttime = start_time.timestamp + (section_id-1)*timedelta(minutes=2, seconds=30)

        endtime = starttime + timedelta(minutes=5)
        logs = DataLog.objects.filter(Q(session=session)&Q(time__gt=starttime)&Q(time__lt=endtime))
        data['starttime'] = starttime
        data['endtime'] = endtime
        data['interval'] = timedelta(minutes=5)
        # need to determine users in roles for session
        positions = UserPosition.objects.filter(session=session)
        bus_names = positions.filter(position__role__name="Business").values_list('user', flat=True)
        ops_names = positions.filter(position__role__name="OpsPlanner").values_list('user', flat=True)
        des_names = positions.filter(position__role__name="Designer").values_list('user', flat=True)

        # assign counts of comms
        data["comms_ops"] = logs.filter(Q(type__contains='chat')&Q(user__in=ops_names)&~Q(type__contains='Help')).count()
        data["comms_design"] = logs.filter(Q(type__contains='chat')&Q(user__in=des_names)&~Q(type__contains='Help')).count()
        data["comms_pm"] = logs.filter(Q(type__contains='chat')&Q(user__in=bus_names)&~Q(type__contains='Help')).count()

        # assign counts of actions
        planner_logs = logs.filter(action__startswith='planner')
        designer_logs = logs.filter(action__startswith='designer')
        act_iter_commands = ['AssemblyChange', 'AssemblyHandle', 'CapacityInput', 'HotKeyComponentToEmpty', 'HotKeyComponentToMotorCCW', 'HotKeyComponentToMotorCW',
            'HotKeyComponentToFoil', 'HotKeyComponentToStructure', 'RemovedComponent', 'RemovedConnector', 'ResetDesign', 'ResetView', 'ScaleDown', 'ScaleUp',
            'ToggleCCWMotor', 'ToggleCWMotor', 'ToggleEmpty', 'ToggleFoil', 'ToggleInfoPanel', 'ToggleStructure']
        act_submit_commands = ['Evaluate', 'Evaluated', 'SubmittingToDB', 'SubmitToDB']
        act_AI_commands = ['RunDesignAgent', 'SelectedAIDesign']
        ops_iter_commands = ['ManualPathAdded', 'ManualPathRemove', 'OrthogonalCamera', 'PathMetrics', 'PerspectiveCamera', 'RemoveAllPaths', 'ResetView',
            'SelectPath', 'ToggleInfoPanel', 'ToggleWeightIcons', 'VehicleDuplicated', ' VehiclePathRemoved', ' VehicleToggle']
        ops_submit_commands = ['SubmitPlanToDB', 'SubmitScenario']
        ops_AI_commands = ['RunPathAgent']
        data["act_ops_iter"] = planner_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in ops_iter_commands])).count()
        data["act_ops_submit"] = planner_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in ops_submit_commands])).count()
        data["act_ops_AI"] = planner_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in ops_AI_commands])).count()
        data["act_design_iter"] = designer_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in act_iter_commands])).count()
        data["act_design_submit"] = designer_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in act_submit_commands])).count()
        data["act_design_AI"] = designer_logs.filter(reduce(lambda x, y: x | y, [Q(action__contains=word) for word in act_AI_commands])).count()
        return(data)

class MediationChatView(APIView):
    """
    Return chat data for mediation
    """
    def get(self, request, session_id, section_id=0, format=None):
        data = self.get_data(session_id, section_id)
        mediationChats = MediationChatSerializer(data)
        return Response(mediationChats.data)


    def get_data(self, session_id, section_id ):
        data ={"session_id" : session_id}
        session = Session.objects.get(id=data["session_id"])
        start_time = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()

        # Calculate the start and end times for the desired interval
        starttime = start_time.timestamp + (section_id-1)*timedelta(minutes=2, seconds=30)

        endtime = starttime + timedelta(minutes=5)
        logs = DataLog.objects.filter(Q(session=session)&Q(time__gt=starttime)&Q(time__lt=endtime))
        data['starttime'] = starttime
        data['endtime'] = endtime
        data['interval'] = timedelta(minutes=5)
        all_stopwords = stopwords.words('english')
        # add any additional stopwords to the current list
        # more_words = ['stop', 'words', 'list']
        # all_stopwords.extend(more_words)
        # need to determine users in roles for session
        parameter_words = ['budget', 'capacity', 'constraint', 'cost', 'customer', 'deliver', 'design', 'distance', 'drone', 'food',
            'house', 'lbs', 'location', 'market', 'mile', 'mph', 'package', 'parameter', 'parcel', 'path', 'payload', 'plan', 'pound',
            'price', 'profit', 'range', 'requirement', 'route', 'speed', 'velocity', 'warehouse', 'weight']
        strategy_words = ['add', 'balance', 'big', 'change', 'cheap', 'cluster', 'combine', 'communicate', 'compare', 'cover', 'create',
            'decrease', 'develop', 'evaluate', 'expand', 'far', 'fast', 'focus', 'generate', 'heavy', 'improve', 'increase', 'integrate',
            'large', 'limit', 'little', 'long', 'lot', 'low', 'maximize', 'operate', 'optimal', 'optimize', 'prioritize', 'quick',
            'reduce', 'refresh', 'sacrifice', 'short', 'small', 'strategy', 'submit', 'update']
        # we need to match the word stems
        parameter_stems = [porter.stem(word) for word in parameter_words]
        strategy_stems = [porter.stem(word) for word in strategy_words]
        roles = ['Business', 'OpsPlanner', 'Designer']
        ups = UserPosition.objects.filter(Q(session=session)&Q(position__role__name__in=roles))
        all_chats=[]
        # word freq is a dictionary that holds a total count of words for each
        wordfreq = {}
        for up in ups:
            # print(up.user)
            user_chats=list(logs.filter(Q(type__contains='chat')&Q(user=up.user)&~Q(type__contains='Help')).values_list('action', flat=True))
            # print(user_chats)
            # tokenize the words and remove punctuation
            tokens = [tokenizer.tokenize(str) for str in user_chats]
            flat_tokens = [item for sublist in tokens for item in sublist]
            # print("tokens with punctation removed")
            # print(flat_tokens)
            # correct the spelling using the Hunspell dictionary implementation
            correct_tokens = self.correctSpelling(flat_tokens)
            # print('spell checked tokens')
            # print(correct_tokens)
            # remove stop words
            good_tokens = [word for word in correct_tokens if not word in all_stopwords]
            # print('nltk stop words removed')
            # print(good_tokens)
            # remove short and long words
            better_tokens = [word for word in good_tokens if len(word)>2 and len(word)<15]
            # print('short and long words removed')
            # print(better_tokens)
            # stem words
            stem_tokens = [porter.stem(word) for word in better_tokens]

            # print("stemmed tokens ")
            # print(stem_tokens)
            # identify distinct words anf count them
            for token in stem_tokens:
                if token not in wordfreq.keys():
                    wordfreq[token] = 1
                else:
                    wordfreq[token] += 1
            all_chats.append(stem_tokens)
        # count parameter and strategy word frequency
        parameter_count = 0
        strategy_count = 0
        for stem in wordfreq.keys():
            if stem in parameter_stems:
                parameter_count += wordfreq[stem]
            if stem in strategy_stems:
                strategy_count += wordfreq[stem]

        # create bag of words matrix and tf-idf matrix
        # we have a complete list of words, a bag of words is a matrix that counts the occurance of each
        # word in each document
        # the tf-idf is the term frequency - inverse document frequency matrix for each word in each document
        # it is simple term count in each document (tf) times the inverse document frequency is the
        # log((total # documents)/(# documents term appears)). The tf-idf is simply the tf * idf
        # assuming the log function is base 10
        tf = np.zeros((len(all_chats), len(wordfreq)))
        i = 0
        j = 0
        for chat in all_chats:
            if len(chat)>0:
                j=0
                for token in wordfreq.keys():
                    tf[i,j] = chat.count(token)
                    j += 1
                i += 1
        total_docs = i
        total_terms = j
        # remove rows of zeros
        tf = np.delete(tf, range(total_docs,len(all_chats)), 0)

        # print('total docs: ', total_docs)
        # print('total terms: ' , total_terms)
        # print('term frequency')
        # print(tf)
        idf = np.log(total_docs/np.count_nonzero(tf, axis=0))
        # idf = total_docs/np.count_nonzero(tf, axis=0)
        # print('inverse document frequency')
        # print(idf)
        tf_idf = tf * idf
        # print(tf_idf.shape)
        # we settled on 2 maximum components (topics) for the semantics metric
        max_comps = 2
        num_comps = np.min((total_terms-1, total_docs, max_comps))
        # print('num_comps: ', num_comps)
        if num_comps>1:
            svd = TruncatedSVD(n_components=num_comps)
            trans = svd.fit_transform(tf_idf)
            # print(tf_idf.shape)
            # print('svd matrix')
            # print(trans.shape)
            # print(trans)

            # pdist returns an array of interpoint distances - not a matrix
            disp = 1 - pdist(trans, 'cosine')
            # to get a matrix, use squareform
            # disp = 1 - squareform(pdist(svd.components_, 'cosine'))
            # print('cosine p-dist')
            # print(squareform(pdist(trans, 'cosine')))

            # print(disp)

            semantics = np.mean(disp)
            # sometimes pdist will come back with NaN, so return a 0.0 if it does
            if np.isnan(semantics):
                semantics = 0.0
        else:
            # noone or only one person talked to no semantics again
            semantics = 0.0

        # print(semantics)

        data['parameter'] = parameter_count
        data['strategy'] = strategy_count
        data['semantics'] = semantics
        return data

    def correctSpelling(self, words):
        # auto-correct words
        enc = spellchecker.get_dic_encoding()
        corrected = []
        for w in words:
            ok = spellchecker.spell(w)   # check spelling
            if not ok:
                suggestions = spellchecker.suggest(w)
                if len(suggestions) > 0:  # there are suggestions
                    best = suggestions[0]
                    corrected.append(best)
                else:
                    corrected.append(w)  # there's no suggestion for a correct word
            else:
                corrected.append(w)   # this word is correct

        return corrected




class SessionDataLog(generics.ListAPIView):
    """
    List all plan entries for the session - short version
    """
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            qs = DataLog.objects.filter(session=st.session, user=user).order_by('time')
        else:
            qs = DataLog.objects.none()
        return qs

    serializer_class = DataLogSerializer


class DataLogDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a DataLog Entry
    """
    queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer

class DataLogListView(generic.ListView):

    def get_queryset(self):
        user = self.request.user
        session = Session.objects.get(id=self.kwargs['session_id'])
        if session:
            log = DataLog.objects.filter(session=session).order_by('-time')
        else:
            log = None
        return log

    def get_context_data(self, **kwargs):
        context = super(DataLogListView, self).get_context_data(**kwargs)
        session = Session.objects.get(id=self.kwargs['session_id'])
        if session:
            context['session_name'] = session.name
        else:
            context['session_name'] = "Unknown"
        return context


    template_name = 'repo/datalog_list.html'




class DLAdminView(generics.ListAPIView):
    queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'repo/datalog_admin.html'


class VDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = VehicleDemo.objects.all()
    serializer_class = VDSerializer

class VDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = VehicleDemo.objects.all()
    serializer_class = VDSerializer

class SDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = ScenarioDemo.objects.all()
    serializer_class = SDSerializer

class SDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = ScenarioDemo.objects.all()
    serializer_class = SDSerializer

class OPDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = OpsPlanDemo.objects.all()
    serializer_class = OPDSerializer

class OPDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = OpsPlanDemo.objects.all()
    serializer_class = OPDSerializer

class PDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = PlayDemo.objects.all()
    serializer_class = PDSerializer

class PDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = PlayDemo.objects.all()
    serializer_class = PDSerializer
