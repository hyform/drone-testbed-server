class Interventions:
    ACTION_1 = "Ops planners, it would be good to continue working on and refining your plans a bit more."
    ACTION_2 = "Hey operations team, I suggest that you try evaluating and submitting your plan and starting fresh."
    ACTION_3 = "Hey operations team, try running the path-planning agent to help."
    ACTION_4 = "Drone designers, it would be helpful if you can continue working on and refining your drone designs a bit more."
    ACTION_5 = "Hey drone design team, I would recommend evaluating and submitting your current design and starting fresh."
    ACTION_6 = "Hey drone design team, check out the suggestions from the drone design agent."
    COMMUNICATION_1 = "Team, I think you should try focusing more on adjusting the design parameters to meet the goals of the problem, and share this with each other (cost, capacity, speed, budget, weight, etc.)."
    COMMUNICATION_2 = "Team, try focusing more on your strategy. Try optimizing and increasing/decreasing size of components, and share this with each other."
    COMMUNICATION_3 = "Hi team, try sharing your goals with each other a bit more and make sure they're aligned."
    COMMUNICATION_4 = "Ops team, please try to communicate with each other more."
    COMMUNICATION_5 = "Drone designers, please try to communicate with each other more."
    COMMUNICATION_6 = "Hi problem manager, please try to communicate with your team more."
    NO_INTERVENTION = "No intervention."

    def add_intervention_constants(context):
        context['ACTION_1'] = Interventions.ACTION_1
        context['ACTION_2'] = Interventions.ACTION_2
        context['ACTION_3'] = Interventions.ACTION_3
        context['ACTION_4'] = Interventions.ACTION_4
        context['ACTION_5'] = Interventions.ACTION_5
        context['ACTION_6'] = Interventions.ACTION_6
        context['COMMUNICATION_1'] = Interventions.COMMUNICATION_1
        context['COMMUNICATION_2'] = Interventions.COMMUNICATION_2
        context['COMMUNICATION_3'] = Interventions.COMMUNICATION_3
        context['COMMUNICATION_4'] = Interventions.COMMUNICATION_4
        context['COMMUNICATION_5'] = Interventions.COMMUNICATION_5
        context['COMMUNICATION_6'] = Interventions.COMMUNICATION_6
        context['NO_INTERVENTION'] = Interventions.NO_INTERVENTION
        return context