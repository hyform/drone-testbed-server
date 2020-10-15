--
-- PostgreSQL database dump
--

-- Dumped from database version 12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.4 (Ubuntu 12.4-0ubuntu0.20.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_designer1; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.ai_designer1 (
    id integer NOT NULL,
    config character varying(500) NOT NULL,
    range double precision NOT NULL,
    cost double precision NOT NULL,
    payload double precision NOT NULL
);


ALTER TABLE public.ai_designer1 OWNER TO atuser;

--
-- Name: ai_designer1_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.ai_designer1_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_designer1_id_seq OWNER TO atuser;

--
-- Name: ai_designer1_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.ai_designer1_id_seq OWNED BY public.ai_designer1.id;


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO atuser;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO atuser;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO atuser;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO atuser;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO atuser;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO atuser;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO atuser;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO atuser;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO atuser;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO atuser;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO atuser;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO atuser;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.authtoken_token OWNER TO atuser;

--
-- Name: chat_channel; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.chat_channel (
    id integer NOT NULL,
    name character varying(25) NOT NULL,
    structure_id integer
);


ALTER TABLE public.chat_channel OWNER TO atuser;

--
-- Name: chat_channel_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.chat_channel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_channel_id_seq OWNER TO atuser;

--
-- Name: chat_channel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.chat_channel_id_seq OWNED BY public.chat_channel.id;


--
-- Name: chat_channelposition; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.chat_channelposition (
    id integer NOT NULL,
    channel_id integer NOT NULL,
    position_id integer NOT NULL
);


ALTER TABLE public.chat_channelposition OWNER TO atuser;

--
-- Name: chat_channelposition_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.chat_channelposition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_channelposition_id_seq OWNER TO atuser;

--
-- Name: chat_channelposition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.chat_channelposition_id_seq OWNED BY public.chat_channelposition.id;


--
-- Name: chat_message; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.chat_message (
    id integer NOT NULL,
    message text NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    channel_id integer NOT NULL,
    sender_id integer NOT NULL,
    session_id integer NOT NULL
);


ALTER TABLE public.chat_message OWNER TO atuser;

--
-- Name: chat_message_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.chat_message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_message_id_seq OWNER TO atuser;

--
-- Name: chat_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.chat_message_id_seq OWNED BY public.chat_message.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO atuser;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO atuser;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO atuser;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO atuser;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO atuser;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO atuser;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO atuser;

--
-- Name: exper_customlinks; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_customlinks (
    id integer NOT NULL,
    text character varying(255) NOT NULL,
    link character varying(2048) NOT NULL,
    link_type integer,
    is_team boolean,
    ai boolean,
    status integer,
    first boolean,
    last boolean,
    org_id integer,
    position_id integer,
    role_id integer,
    structure_id integer
);


ALTER TABLE public.exper_customlinks OWNER TO atuser;

--
-- Name: exper_customlinks_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_customlinks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_customlinks_id_seq OWNER TO atuser;

--
-- Name: exper_customlinks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_customlinks_id_seq OWNED BY public.exper_customlinks.id;


--
-- Name: exper_exercise; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_exercise (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    experiment_id integer
);


ALTER TABLE public.exper_exercise OWNER TO atuser;

--
-- Name: exper_exercise_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_exercise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_exercise_id_seq OWNER TO atuser;

--
-- Name: exper_exercise_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_exercise_id_seq OWNED BY public.exper_exercise.id;


--
-- Name: exper_experiment; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_experiment (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    study_id integer NOT NULL,
    user_id integer
);


ALTER TABLE public.exper_experiment OWNER TO atuser;

--
-- Name: exper_experiment_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_experiment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_experiment_id_seq OWNER TO atuser;

--
-- Name: exper_experiment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_experiment_id_seq OWNED BY public.exper_experiment.id;


--
-- Name: exper_group; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_group (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    structure_id integer NOT NULL
);


ALTER TABLE public.exper_group OWNER TO atuser;

--
-- Name: exper_group_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_group_id_seq OWNER TO atuser;

--
-- Name: exper_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_group_id_seq OWNED BY public.exper_group.id;


--
-- Name: exper_groupposition; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_groupposition (
    id integer NOT NULL,
    group_id integer NOT NULL,
    position_id integer NOT NULL,
    "primary" boolean NOT NULL
);


ALTER TABLE public.exper_groupposition OWNER TO atuser;

--
-- Name: exper_groupposition_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_groupposition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_groupposition_id_seq OWNER TO atuser;

--
-- Name: exper_groupposition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_groupposition_id_seq OWNED BY public.exper_groupposition.id;


--
-- Name: exper_market; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_market (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.exper_market OWNER TO atuser;

--
-- Name: exper_market_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_market_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_market_id_seq OWNER TO atuser;

--
-- Name: exper_market_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_market_id_seq OWNED BY public.exper_market.id;


--
-- Name: exper_organization; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_organization (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.exper_organization OWNER TO atuser;

--
-- Name: exper_organization_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_organization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_organization_id_seq OWNER TO atuser;

--
-- Name: exper_organization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_organization_id_seq OWNED BY public.exper_organization.id;


--
-- Name: exper_position; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_position (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    role_id integer NOT NULL,
    structure_id integer NOT NULL
);


ALTER TABLE public.exper_position OWNER TO atuser;

--
-- Name: exper_position_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_position_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_position_id_seq OWNER TO atuser;

--
-- Name: exper_position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_position_id_seq OWNED BY public.exper_position.id;


--
-- Name: exper_role; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_role (
    id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.exper_role OWNER TO atuser;

--
-- Name: exper_role_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_role_id_seq OWNER TO atuser;

--
-- Name: exper_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_role_id_seq OWNED BY public.exper_role.id;


--
-- Name: exper_session; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_session (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    use_ai boolean NOT NULL,
    status integer NOT NULL,
    experiment_id integer,
    market_id integer NOT NULL,
    prior_session_id integer,
    structure_id integer NOT NULL,
    index integer NOT NULL,
    exercise_id integer
);


ALTER TABLE public.exper_session OWNER TO atuser;

--
-- Name: exper_session_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_session_id_seq OWNER TO atuser;

--
-- Name: exper_session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_session_id_seq OWNED BY public.exper_session.id;


--
-- Name: exper_sessionteam; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_sessionteam (
    id integer NOT NULL,
    session_id integer NOT NULL,
    team_id integer NOT NULL
);


ALTER TABLE public.exper_sessionteam OWNER TO atuser;

--
-- Name: exper_sessionteam_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_sessionteam_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_sessionteam_id_seq OWNER TO atuser;

--
-- Name: exper_sessionteam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_sessionteam_id_seq OWNED BY public.exper_sessionteam.id;


--
-- Name: exper_structure; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_structure (
    id integer NOT NULL,
    name character varying(25) NOT NULL,
    organization_id integer
);


ALTER TABLE public.exper_structure OWNER TO atuser;

--
-- Name: exper_structure_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_structure_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_structure_id_seq OWNER TO atuser;

--
-- Name: exper_structure_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_structure_id_seq OWNED BY public.exper_structure.id;


--
-- Name: exper_study; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_study (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    purpose text NOT NULL,
    lead character varying(50) NOT NULL,
    organization_id integer
);


ALTER TABLE public.exper_study OWNER TO atuser;

--
-- Name: exper_study_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_study_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_study_id_seq OWNER TO atuser;

--
-- Name: exper_study_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_study_id_seq OWNED BY public.exper_study.id;


--
-- Name: exper_userchecklist; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_userchecklist (
    id integer NOT NULL,
    precheck boolean NOT NULL,
    postcheck boolean NOT NULL,
    session_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.exper_userchecklist OWNER TO atuser;

--
-- Name: exper_userchecklist_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_userchecklist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_userchecklist_id_seq OWNER TO atuser;

--
-- Name: exper_userchecklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_userchecklist_id_seq OWNED BY public.exper_userchecklist.id;


--
-- Name: exper_userposition; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.exper_userposition (
    id integer NOT NULL,
    position_id integer NOT NULL,
    user_id integer NOT NULL,
    session_id integer
);


ALTER TABLE public.exper_userposition OWNER TO atuser;

--
-- Name: exper_userposition_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.exper_userposition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exper_userposition_id_seq OWNER TO atuser;

--
-- Name: exper_userposition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.exper_userposition_id_seq OWNED BY public.exper_userposition.id;


--
-- Name: repo_address; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_address (
    id integer NOT NULL,
    x double precision NOT NULL,
    z double precision NOT NULL,
    region character varying(20) NOT NULL
);


ALTER TABLE public.repo_address OWNER TO atuser;

--
-- Name: repo_address_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_address_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_address_id_seq OWNER TO atuser;

--
-- Name: repo_address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_address_id_seq OWNED BY public.repo_address.id;


--
-- Name: repo_customer; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_customer (
    id integer NOT NULL,
    market_id integer NOT NULL,
    payload character varying(20) NOT NULL,
    weight double precision NOT NULL,
    address_id integer NOT NULL
);


ALTER TABLE public.repo_customer OWNER TO atuser;

--
-- Name: repo_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_customer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_customer_id_seq OWNER TO atuser;

--
-- Name: repo_customer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_customer_id_seq OWNED BY public.repo_customer.id;


--
-- Name: repo_customerscenario; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_customerscenario (
    id integer NOT NULL,
    selected boolean NOT NULL,
    customer_id integer NOT NULL,
    scenario_id integer NOT NULL
);


ALTER TABLE public.repo_customerscenario OWNER TO atuser;

--
-- Name: repo_customerlist_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_customerlist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_customerlist_id_seq OWNER TO atuser;

--
-- Name: repo_customerlist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_customerlist_id_seq OWNED BY public.repo_customerscenario.id;


--
-- Name: repo_datalog; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_datalog (
    id integer NOT NULL,
    user_id integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    action text NOT NULL,
    session_id integer,
    type character varying(255) NOT NULL
);


ALTER TABLE public.repo_datalog OWNER TO atuser;

--
-- Name: repo_datalog_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_datalog_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_datalog_id_seq OWNER TO atuser;

--
-- Name: repo_datalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_datalog_id_seq OWNED BY public.repo_datalog.id;


--
-- Name: repo_designteam; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_designteam (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    initialscore double precision NOT NULL,
    currentscore double precision NOT NULL,
    organization_id integer
);


ALTER TABLE public.repo_designteam OWNER TO atuser;

--
-- Name: repo_designteam_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_designteam_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_designteam_id_seq OWNER TO atuser;

--
-- Name: repo_designteam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_designteam_id_seq OWNED BY public.repo_designteam.id;


--
-- Name: repo_experorg; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_experorg (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.repo_experorg OWNER TO atuser;

--
-- Name: repo_experorg_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_experorg_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_experorg_id_seq OWNER TO atuser;

--
-- Name: repo_experorg_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_experorg_id_seq OWNED BY public.repo_experorg.id;


--
-- Name: repo_opsplandemo; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_opsplandemo (
    id integer NOT NULL,
    xmlstring text NOT NULL,
    tag character varying(50) NOT NULL,
    team character varying(50) NOT NULL
);


ALTER TABLE public.repo_opsplandemo OWNER TO atuser;

--
-- Name: repo_opsplandemo_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_opsplandemo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_opsplandemo_id_seq OWNER TO atuser;

--
-- Name: repo_opsplandemo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_opsplandemo_id_seq OWNED BY public.repo_opsplandemo.id;


--
-- Name: repo_path; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_path (
    id integer NOT NULL,
    leavetime double precision NOT NULL,
    returntime double precision NOT NULL,
    vehicle_id integer NOT NULL,
    warehouse_id integer NOT NULL,
    group_id integer,
    session_id integer,
    plan_id integer
);


ALTER TABLE public.repo_path OWNER TO atuser;

--
-- Name: repo_path_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_path_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_path_id_seq OWNER TO atuser;

--
-- Name: repo_path_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_path_id_seq OWNED BY public.repo_path.id;


--
-- Name: repo_pathcustomer; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_pathcustomer (
    id integer NOT NULL,
    customer_id integer NOT NULL,
    path_id integer NOT NULL,
    stop integer NOT NULL
);


ALTER TABLE public.repo_pathcustomer OWNER TO atuser;

--
-- Name: repo_pathcustomer_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_pathcustomer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_pathcustomer_id_seq OWNER TO atuser;

--
-- Name: repo_pathcustomer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_pathcustomer_id_seq OWNED BY public.repo_pathcustomer.id;


--
-- Name: repo_plan; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_plan (
    id integer NOT NULL,
    tag character varying(100) NOT NULL,
    scenario_id integer NOT NULL,
    group_id integer,
    session_id integer
);


ALTER TABLE public.repo_plan OWNER TO atuser;

--
-- Name: repo_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_plan_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_plan_id_seq OWNER TO atuser;

--
-- Name: repo_plan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_plan_id_seq OWNED BY public.repo_plan.id;


--
-- Name: repo_playdemo; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_playdemo (
    id integer NOT NULL,
    xmlstring text NOT NULL,
    tag character varying(50) NOT NULL,
    team character varying(50) NOT NULL
);


ALTER TABLE public.repo_playdemo OWNER TO atuser;

--
-- Name: repo_playdemo_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_playdemo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_playdemo_id_seq OWNER TO atuser;

--
-- Name: repo_playdemo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_playdemo_id_seq OWNED BY public.repo_playdemo.id;


--
-- Name: repo_profile; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_profile (
    id integer NOT NULL,
    team_id integer,
    user_id integer NOT NULL,
    is_exper boolean NOT NULL,
    organization_id integer,
    user_type integer NOT NULL,
    experiment_id integer,
    study_id integer,
    temp_code text NOT NULL
);


ALTER TABLE public.repo_profile OWNER TO atuser;

--
-- Name: repo_profile_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_profile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_profile_id_seq OWNER TO atuser;

--
-- Name: repo_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_profile_id_seq OWNED BY public.repo_profile.id;


--
-- Name: repo_scenario; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_scenario (
    id integer NOT NULL,
    tag character varying(100) NOT NULL,
    warehouse_id integer NOT NULL,
    group_id integer,
    session_id integer,
    version integer NOT NULL
);


ALTER TABLE public.repo_scenario OWNER TO atuser;

--
-- Name: repo_scenario_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_scenario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_scenario_id_seq OWNER TO atuser;

--
-- Name: repo_scenario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_scenario_id_seq OWNED BY public.repo_scenario.id;


--
-- Name: repo_scenariodemo; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_scenariodemo (
    id integer NOT NULL,
    xmlstring text NOT NULL,
    tag character varying(50) NOT NULL,
    team character varying(50) NOT NULL
);


ALTER TABLE public.repo_scenariodemo OWNER TO atuser;

--
-- Name: repo_scenariodemo_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_scenariodemo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_scenariodemo_id_seq OWNER TO atuser;

--
-- Name: repo_scenariodemo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_scenariodemo_id_seq OWNED BY public.repo_scenariodemo.id;


--
-- Name: repo_vehicle; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_vehicle (
    id integer NOT NULL,
    tag character varying(100) NOT NULL,
    config text NOT NULL,
    result character varying(100) NOT NULL,
    range double precision NOT NULL,
    velocity double precision NOT NULL,
    cost double precision NOT NULL,
    payload double precision NOT NULL,
    group_id integer NOT NULL,
    session_id integer NOT NULL
);


ALTER TABLE public.repo_vehicle OWNER TO atuser;

--
-- Name: repo_vehicle_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_vehicle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_vehicle_id_seq OWNER TO atuser;

--
-- Name: repo_vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_vehicle_id_seq OWNED BY public.repo_vehicle.id;


--
-- Name: repo_vehicledemo; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_vehicledemo (
    id integer NOT NULL,
    xmlstring text NOT NULL,
    tag character varying(50) NOT NULL,
    team character varying(50) NOT NULL
);


ALTER TABLE public.repo_vehicledemo OWNER TO atuser;

--
-- Name: repo_vehicledemo_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_vehicledemo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_vehicledemo_id_seq OWNER TO atuser;

--
-- Name: repo_vehicledemo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_vehicledemo_id_seq OWNED BY public.repo_vehicledemo.id;


--
-- Name: repo_warehouse; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_warehouse (
    id integer NOT NULL,
    address_id integer NOT NULL,
    group_id integer,
    session_id integer
);


ALTER TABLE public.repo_warehouse OWNER TO atuser;

--
-- Name: repo_warehouse_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_warehouse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_warehouse_id_seq OWNER TO atuser;

--
-- Name: repo_warehouse_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_warehouse_id_seq OWNED BY public.repo_warehouse.id;


--
-- Name: repo_waypoint; Type: TABLE; Schema: public; Owner: atuser
--

CREATE TABLE public.repo_waypoint (
    id integer NOT NULL,
    deliverytime double precision NOT NULL,
    customer_id integer NOT NULL
);


ALTER TABLE public.repo_waypoint OWNER TO atuser;

--
-- Name: repo_waypoint_id_seq; Type: SEQUENCE; Schema: public; Owner: atuser
--

CREATE SEQUENCE public.repo_waypoint_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.repo_waypoint_id_seq OWNER TO atuser;

--
-- Name: repo_waypoint_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: atuser
--

ALTER SEQUENCE public.repo_waypoint_id_seq OWNED BY public.repo_waypoint.id;


--
-- Name: ai_designer1 id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.ai_designer1 ALTER COLUMN id SET DEFAULT nextval('public.ai_designer1_id_seq'::regclass);


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: chat_channel id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channel ALTER COLUMN id SET DEFAULT nextval('public.chat_channel_id_seq'::regclass);


--
-- Name: chat_channelposition id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channelposition ALTER COLUMN id SET DEFAULT nextval('public.chat_channelposition_id_seq'::regclass);


--
-- Name: chat_message id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_message ALTER COLUMN id SET DEFAULT nextval('public.chat_message_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: exper_customlinks id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks ALTER COLUMN id SET DEFAULT nextval('public.exper_customlinks_id_seq'::regclass);


--
-- Name: exper_exercise id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_exercise ALTER COLUMN id SET DEFAULT nextval('public.exper_exercise_id_seq'::regclass);


--
-- Name: exper_experiment id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_experiment ALTER COLUMN id SET DEFAULT nextval('public.exper_experiment_id_seq'::regclass);


--
-- Name: exper_group id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_group ALTER COLUMN id SET DEFAULT nextval('public.exper_group_id_seq'::regclass);


--
-- Name: exper_groupposition id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_groupposition ALTER COLUMN id SET DEFAULT nextval('public.exper_groupposition_id_seq'::regclass);


--
-- Name: exper_market id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_market ALTER COLUMN id SET DEFAULT nextval('public.exper_market_id_seq'::regclass);


--
-- Name: exper_organization id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_organization ALTER COLUMN id SET DEFAULT nextval('public.exper_organization_id_seq'::regclass);


--
-- Name: exper_position id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_position ALTER COLUMN id SET DEFAULT nextval('public.exper_position_id_seq'::regclass);


--
-- Name: exper_role id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_role ALTER COLUMN id SET DEFAULT nextval('public.exper_role_id_seq'::regclass);


--
-- Name: exper_session id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session ALTER COLUMN id SET DEFAULT nextval('public.exper_session_id_seq'::regclass);


--
-- Name: exper_sessionteam id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_sessionteam ALTER COLUMN id SET DEFAULT nextval('public.exper_sessionteam_id_seq'::regclass);


--
-- Name: exper_structure id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_structure ALTER COLUMN id SET DEFAULT nextval('public.exper_structure_id_seq'::regclass);


--
-- Name: exper_study id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_study ALTER COLUMN id SET DEFAULT nextval('public.exper_study_id_seq'::regclass);


--
-- Name: exper_userchecklist id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userchecklist ALTER COLUMN id SET DEFAULT nextval('public.exper_userchecklist_id_seq'::regclass);


--
-- Name: exper_userposition id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userposition ALTER COLUMN id SET DEFAULT nextval('public.exper_userposition_id_seq'::regclass);


--
-- Name: repo_address id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_address ALTER COLUMN id SET DEFAULT nextval('public.repo_address_id_seq'::regclass);


--
-- Name: repo_customer id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customer ALTER COLUMN id SET DEFAULT nextval('public.repo_customer_id_seq'::regclass);


--
-- Name: repo_customerscenario id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customerscenario ALTER COLUMN id SET DEFAULT nextval('public.repo_customerlist_id_seq'::regclass);


--
-- Name: repo_datalog id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_datalog ALTER COLUMN id SET DEFAULT nextval('public.repo_datalog_id_seq'::regclass);


--
-- Name: repo_designteam id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_designteam ALTER COLUMN id SET DEFAULT nextval('public.repo_designteam_id_seq'::regclass);


--
-- Name: repo_experorg id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_experorg ALTER COLUMN id SET DEFAULT nextval('public.repo_experorg_id_seq'::regclass);


--
-- Name: repo_opsplandemo id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_opsplandemo ALTER COLUMN id SET DEFAULT nextval('public.repo_opsplandemo_id_seq'::regclass);


--
-- Name: repo_path id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path ALTER COLUMN id SET DEFAULT nextval('public.repo_path_id_seq'::regclass);


--
-- Name: repo_pathcustomer id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_pathcustomer ALTER COLUMN id SET DEFAULT nextval('public.repo_pathcustomer_id_seq'::regclass);


--
-- Name: repo_plan id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_plan ALTER COLUMN id SET DEFAULT nextval('public.repo_plan_id_seq'::regclass);


--
-- Name: repo_playdemo id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_playdemo ALTER COLUMN id SET DEFAULT nextval('public.repo_playdemo_id_seq'::regclass);


--
-- Name: repo_profile id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile ALTER COLUMN id SET DEFAULT nextval('public.repo_profile_id_seq'::regclass);


--
-- Name: repo_scenario id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenario ALTER COLUMN id SET DEFAULT nextval('public.repo_scenario_id_seq'::regclass);


--
-- Name: repo_scenariodemo id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenariodemo ALTER COLUMN id SET DEFAULT nextval('public.repo_scenariodemo_id_seq'::regclass);


--
-- Name: repo_vehicle id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicle ALTER COLUMN id SET DEFAULT nextval('public.repo_vehicle_id_seq'::regclass);


--
-- Name: repo_vehicledemo id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicledemo ALTER COLUMN id SET DEFAULT nextval('public.repo_vehicledemo_id_seq'::regclass);


--
-- Name: repo_warehouse id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_warehouse ALTER COLUMN id SET DEFAULT nextval('public.repo_warehouse_id_seq'::regclass);


--
-- Name: repo_waypoint id; Type: DEFAULT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_waypoint ALTER COLUMN id SET DEFAULT nextval('public.repo_waypoint_id_seq'::regclass);


--
-- Data for Name: ai_designer1; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.ai_designer1 (id, config, range, cost, payload) FROM stdin;
100	*aMM0++*bNM3*cMN3*dLM3*eML3*fOM2+*gMO1+*hKM2*iMK1*jPM2+*kMP1+*lJM2+*mMJ1+^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,11,3	13.543988	3084.5044	11
101	*aMM0+++*bNM3*cMN3*dLM3*eML3*fOM4*gNN4*hNL4*iMO4*jLN4*kKM4*lLL4*mMK4*nPM2++*oMP1++*pJM2++*qMJ1++^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^fn^io^kp^mq^cg^eh^el,9,3	15.27944	3091.7625	9
102	*aMM0+*bNM3*cMN3*dLM3+*eML3+*fOM2++*gMO1++*hKM2++*iMK1++*jPM2*kMP1*lJM2*mMJ1^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,11,3	11.40136	3001.9343	11
103	*aMM0+++++++*bNM3+++*cMN3++*dLM3++*eML3++*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,18,3	13.807518	4379.8286	18
104	*aMM0++++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,21,3	11.014151	4055.027	21
105	*aMM0++++++*bNM3++*cMN3++*dLM3++*eML3++*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,21,3	11.039756	4092.2622	21
106	*aMM0+++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^el^em^cg^dj^eh,19,3	16.206049	7167.871	19
107	*aMM0+++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gMO4*hKM4*iMK4*jPM4*kON4*lOL4*mNO4*nMP4*oLO4*pKN4*qJM4*rKL4*sNK4*tLK4*uMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^fk^fl^gm^gn^go^hp^hq^hr^is^it^iu,19,3	15.848154	7007.6694	19
108	*aMM0+++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^dj^dk^dl^em^cg^el,17,3	16.913406	7167.871	17
109	*aMM0++++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL4*iMO4*jLN4*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^eh^el,19,3	16.36555	7481.7295	19
110	*aMM0++++++*bNM3++*cMN3++*dLM3++*eML3++*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,20,3	11.454496	4092.2622	20
111	*aMM0++++++*bNM3++*cMN3++*dLM3++*eML3++*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kON4*lOL4*mNO4*nMP4*oLO4*pKN4*qJM4*rKL4*sNK4*tLK4*uMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^fk^fl^gm^gn^go^hp^hq^hr^is^it^iu,19,3	12.460136	4092.2622	19
112	*aMM0+++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fNN3*gLL3^ab^ac^ad^ae^cf^eg,15,3	13.139071	4177.4785	15
113	*aMM0++++++*bNM3+++*cMN3+++*dLM3+*eML3+*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,21,3	11.123908	4092.6096	21
114	*aMM0++++++*bNM3++*cMN3+*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,22,3	10.81561	4068.905	22
115	*aMM0++++++*bNM3+*cMN3+*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,24,3	9.350168	4064.1653	24
116	*aMM0+*bNM3*cMN3*dLM3*eML3*fOM4*gMO4*hKM4*iMK4*jPM2++*kMP1++*lJM2++*mMJ1++^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,8,3	23.003311	2680.796	8
117	*aMM0+*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4*nPM4*oMP4*pJM4*qMJ4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^fn^io^kp^mq^cg^dj^el,7,3	14.915645	2361.3445	7
118	*aMM0+*bNM3*cMN3*dLM3*eML3*fOM2++*gMO1++*hKM2++*iMK1++^ab^ac^ad^ae^bf^cg^dh^ei,9,3	12.608813	2680.796	9
119	*aMM0++*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^dj,10,3	10.896672	2558.928	10
120	*aMM0+*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^el^em^cg^dj^eh,6,3	17.818705	2361.3445	6
121	*aMM0+*bNM3*cMN3*dLM3*eML3*fOM4*gMO4*hKM4*iMK4*jPM2++*kMP1++*lJM2++*mMJ1++^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,8,3	23.003311	2680.796	8
122	*aMM0+++++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,20,3	12.506371	4337.68	20
123	*aMM0+++++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,19,3	12.86285	4337.68	19
124	*aMM0+++++++*bNM3++*cMN3+*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,18,3	13.422877	4351.558	18
125	*aMM0++++++++*bNM4*cMN4*dLM4*eML4*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,41,3	4.6293745	4318.766	41
126	*aMM0++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^dj^dk^dl^em^eh^el,30,3	8.055374	4478.968	30
127	*aMM0+++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL4*iMO4*jLN4*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^el^em^cg^dj^eh,32,3	7.5412645	4639.7007	32
128	*aMM0+++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,34,3	7.070363	4639.7007	34
129	*aMM0+++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,38,3	6.1708956	4639.7007	38
130	*aMM0++++*bNM3+*cMN3+*dLM3+*eML3+*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,23,3	7.3369784	3562.0776	23
131	*aMM0+++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kON4*lOL4*mNO4*nMP4*oLO4*pKN4*qJM4*rKL4*sNK4*tLK4*uMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^fk^fl^gm^gn^go^hp^hq^hr^is^it^iu,23,3	9.002437	3790.6033	23
132	*aMM0++++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,23,3	9.651187	4055.027	23
133	*aMM0+++++++*bNM2++*cMN1++*dLM2++*eML1++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^eh^el,18,3	10.709842	3955.2285	18
134	*aMM0+++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fNN3++*gLL3++^ab^ac^ad^ae^cf^eg,15,3	14.055558	4196.096	15
135	*aMM0+++++++++++*bNM2++++*cMN1++++*dLM2++++*eML1++++*fNN3++*gLL3++^ab^ac^ad^ae^cf^eg,11,3	21.652092	5816.903	11
136	*aMM0++++++++*bNM3*cMN3*dLM3*eML3*fOM2+++*gMO1+++*hKM2+++*iMK1+++*jPM4*kMP4*lJM4*mMJ4^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,16,3	15.075813	4639.169	16
137	*aMM0+++++++++*bNM3+++*cMN3+++*dLM3+++*eML3+++*fOM2+++*gMO1+++*hKM2+++*iMK1+++^ab^ac^ad^ae^bf^cg^dh^ei,14,3	17.181198	5016.992	14
138	*aMM0++*bNM3*cMN3*dLM3*eML3*fOM2+*gMO1+*hKM2*iMK1*jPM2+*kMP1+*lJM2+*mMJ1+^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,11,3	13.543988	3084.5044	11
139	*aMM0*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^dj^el,6,3	17.446821	2178.9517	6
140	*aMM0+*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^eh^el,10,3	7.0306435	2361.3445	10
141	*aMM0++*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^dj,10,3	10.896672	2558.928	10
142	*aMM0+*bNM3*cMN3*dLM3*eML3*fOM2+*gMO1+*hKM2*iMK1*jPM2+*kMP1+*lJM2+*mMJ1+^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,11,3	11.255534	2886.921	11
143	*aMM0*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^dj^eh,8,3	9.933406	2178.9517	8
144	*aMM0+*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^el,8,3	12.263235	2361.3445	8
145	*aMM0++*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4*nPM2*oMP1*pJM2*qMJ1^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^el^em^fn^io^kp^mq^cg^dj^eh,13,3	9.681664	2870.928	13
146	*aMM0++++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^eh^el,17,3	17.276598	7641.9307	17
147	*aMM0++++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL4*iMO4*jLN4*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^cg^eh^el,19,3	16.36555	7481.7295	19
148	*aMM0++++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4^ab^ac^ad^ae^bf^bg^bh^ci^dj^dk^dl^em^cg^eh,20,3	16.217701	7641.9307	20
149	*aMM0+*bNM2+*cMN1+*dLM2+*eML1+*fOM4*gNN4*hNL3*iMO4*jLN3*kKM4*lLL4*mMK4*nPM4*oMP4*pJM4*qMJ4^ab^ac^ad^ae^bf^bg^bh^ci^cj^dk^dl^em^fn^io^kp^mq^cg^dj^el,7,3	14.915645	2361.3445	7
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add Token	7	add_token
26	Can change Token	7	change_token
27	Can delete Token	7	delete_token
28	Can view Token	7	view_token
29	Can add address	8	add_address
30	Can change address	8	change_address
31	Can delete address	8	delete_address
32	Can view address	8	view_address
33	Can add customer	9	add_customer
34	Can change customer	9	change_customer
35	Can delete customer	9	delete_customer
36	Can view customer	9	view_customer
37	Can add design team	10	add_designteam
38	Can change design team	10	change_designteam
39	Can delete design team	10	delete_designteam
40	Can view design team	10	view_designteam
41	Can add ops plan demo	11	add_opsplandemo
42	Can change ops plan demo	11	change_opsplandemo
43	Can delete ops plan demo	11	delete_opsplandemo
44	Can view ops plan demo	11	view_opsplandemo
45	Can add path	12	add_path
46	Can change path	12	change_path
47	Can delete path	12	delete_path
48	Can view path	12	view_path
49	Can add play demo	13	add_playdemo
50	Can change play demo	13	change_playdemo
51	Can delete play demo	13	delete_playdemo
52	Can view play demo	13	view_playdemo
53	Can add scenario demo	14	add_scenariodemo
54	Can change scenario demo	14	change_scenariodemo
55	Can delete scenario demo	14	delete_scenariodemo
56	Can view scenario demo	14	view_scenariodemo
57	Can add vehicle demo	15	add_vehicledemo
58	Can change vehicle demo	15	change_vehicledemo
59	Can delete vehicle demo	15	delete_vehicledemo
60	Can view vehicle demo	15	view_vehicledemo
61	Can add waypoint	16	add_waypoint
62	Can change waypoint	16	change_waypoint
63	Can delete waypoint	16	delete_waypoint
64	Can view waypoint	16	view_waypoint
65	Can add warehouse	17	add_warehouse
66	Can change warehouse	17	change_warehouse
67	Can delete warehouse	17	delete_warehouse
68	Can view warehouse	17	view_warehouse
69	Can add vehicle	18	add_vehicle
70	Can change vehicle	18	change_vehicle
71	Can delete vehicle	18	delete_vehicle
72	Can view vehicle	18	view_vehicle
73	Can add scenario	19	add_scenario
74	Can change scenario	19	change_scenario
75	Can delete scenario	19	delete_scenario
76	Can view scenario	19	view_scenario
77	Can add plan	20	add_plan
78	Can change plan	20	change_plan
79	Can delete plan	20	delete_plan
80	Can view plan	20	view_plan
81	Can add data log	21	add_datalog
82	Can change data log	21	change_datalog
83	Can delete data log	21	delete_datalog
84	Can view data log	21	view_datalog
85	Can add profile	22	add_profile
86	Can change profile	22	change_profile
87	Can delete profile	22	delete_profile
88	Can view profile	22	view_profile
89	Can add path customer	23	add_pathcustomer
90	Can change path customer	23	change_pathcustomer
91	Can delete path customer	23	delete_pathcustomer
92	Can view path customer	23	view_pathcustomer
93	Can add customer scenario	24	add_customerscenario
94	Can change customer scenario	24	change_customerscenario
95	Can delete customer scenario	24	delete_customerscenario
96	Can view customer scenario	24	view_customerscenario
97	Can add designer1	25	add_designer1
98	Can change designer1	25	change_designer1
99	Can delete designer1	25	delete_designer1
100	Can view designer1	25	view_designer1
101	Can add channel	26	add_channel
102	Can change channel	26	change_channel
103	Can delete channel	26	delete_channel
104	Can view channel	26	view_channel
105	Can add message	27	add_message
106	Can change message	27	change_message
107	Can delete message	27	delete_message
108	Can view message	27	view_message
109	Can add channel position	28	add_channelposition
110	Can change channel position	28	change_channelposition
111	Can delete channel position	28	delete_channelposition
112	Can view channel position	28	view_channelposition
113	Can add experiment	29	add_experiment
114	Can change experiment	29	change_experiment
115	Can delete experiment	29	delete_experiment
116	Can view experiment	29	view_experiment
117	Can add group	30	add_group
118	Can change group	30	change_group
119	Can delete group	30	delete_group
120	Can view group	30	view_group
121	Can add market	31	add_market
122	Can change market	31	change_market
123	Can delete market	31	delete_market
124	Can view market	31	view_market
125	Can add position	32	add_position
126	Can change position	32	change_position
127	Can delete position	32	delete_position
128	Can view position	32	view_position
129	Can add role	33	add_role
130	Can change role	33	change_role
131	Can delete role	33	delete_role
132	Can view role	33	view_role
133	Can add session	34	add_session
134	Can change session	34	change_session
135	Can delete session	34	delete_session
136	Can view session	34	view_session
137	Can add structure	35	add_structure
138	Can change structure	35	change_structure
139	Can delete structure	35	delete_structure
140	Can view structure	35	view_structure
141	Can add study	36	add_study
142	Can change study	36	change_study
143	Can delete study	36	delete_study
144	Can view study	36	view_study
145	Can add user position	37	add_userposition
146	Can change user position	37	change_userposition
147	Can delete user position	37	delete_userposition
148	Can view user position	37	view_userposition
149	Can add session team	38	add_sessionteam
150	Can change session team	38	change_sessionteam
151	Can delete session team	38	delete_sessionteam
152	Can view session team	38	view_sessionteam
153	Can add group position	39	add_groupposition
154	Can change group position	39	change_groupposition
155	Can delete group position	39	delete_groupposition
156	Can view group position	39	view_groupposition
157	Can add organization	40	add_organization
158	Can change organization	40	change_organization
159	Can delete organization	40	delete_organization
160	Can view organization	40	view_organization
161	Can add user checklist	41	add_userchecklist
162	Can change user checklist	41	change_userchecklist
163	Can delete user checklist	41	delete_userchecklist
164	Can view user checklist	41	view_userchecklist
165	Can add token	42	add_tokenproxy
166	Can change token	42	change_tokenproxy
167	Can delete token	42	delete_tokenproxy
168	Can view token	42	view_tokenproxy
169	Can add exper org	43	add_experorg
170	Can change exper org	43	change_experorg
171	Can delete exper org	43	delete_experorg
172	Can view exper org	43	view_experorg
173	Can add custom links	44	add_customlinks
174	Can change custom links	44	change_customlinks
175	Can delete custom links	44	delete_customlinks
176	Can view custom links	44	view_customlinks
177	Can add exercise	45	add_exercise
178	Can change exercise	45	change_exercise
179	Can delete exercise	45	delete_exercise
180	Can view exercise	45	view_exercise
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
3	pbkdf2_sha256$180000$c7nMq5gev1Ne$glYr5puokDb3XqQVOvuHmwfF5Ux1xy7ikaqi7/Feu7M=	\N	f	user-11				f	t	2020-05-19 23:18:11+00
4	pbkdf2_sha256$180000$cHmFiWBWFYy0$qQu/zoqiRuH4xkCJBQFUhGiDvKwQ0ZjmvZbX3L9WRyc=	\N	f	user-12				f	t	2020-05-19 23:18:33+00
5	pbkdf2_sha256$180000$4KQ8IupTu2DJ$60pn2rkXxE4zIOPExtSt3iey2cCsK4ACB5NXLabgwj0=	\N	f	user-13				f	t	2020-05-19 23:18:51+00
6	pbkdf2_sha256$180000$hhv0WKT5MG3m$7b1X7QBQQbb6Giyc3um94Cgvw4+LzD8zhhTfikVD96I=	\N	f	user-14				f	t	2020-05-19 23:19:07+00
7	pbkdf2_sha256$180000$IgEMTVRxJGhp$pbxI+tVNovd4eyahhcToFCF8VCmiDbyx6m5zEspthWU=	\N	f	user-15				f	t	2020-05-19 23:19:27+00
8	pbkdf2_sha256$180000$WE5n7Bu2eKdy$6qcxhxGsx2i/jh3cllloovO8ctRpTU4sEI0qP9qxBe4=	\N	f	user-16				f	t	2020-05-19 23:19:45+00
9	pbkdf2_sha256$180000$o06YtTKkuSH1$fwLlFAOBH5m03U/mQ1ZUsNM1tdOW/8DegGtihyDhTpM=	\N	f	user-21				f	t	2020-05-19 23:19:59+00
10	pbkdf2_sha256$180000$qvWktTUCwfzd$ndNjQ6TLa+cY21NnaXiYdOi7MPGSWhDe2/Eftxof+Qs=	\N	f	user-22				f	t	2020-05-19 23:20:16+00
11	pbkdf2_sha256$180000$EtT7LkoyNSnt$z6Pf2W36KtB/J1E5VcxsXhLqEwVpNSo95KnatFk8CC4=	\N	f	user-23				f	t	2020-05-19 23:20:32+00
12	pbkdf2_sha256$180000$pS7URA0WeezX$fI0w65jpVR3AzU73y2FcnVo9rM68Uu27csvqHMXIU5I=	\N	f	user-24				f	t	2020-05-19 23:20:48+00
13	pbkdf2_sha256$180000$MQPuhUoSScCt$lEmxby2yeIbCOS5TJNPA4GeSH8wdM85lAmvTuiA0ghQ=	\N	f	user-25				f	t	2020-05-19 23:21:06+00
14	pbkdf2_sha256$180000$eRhnPjlBBcut$5qpvDzr5P2AD5xL3H661AXtuHPTyxTMwbKSCA/8Lev4=	\N	f	user-26				f	t	2020-05-19 23:21:24+00
15	pbkdf2_sha256$150000$WbLmXTE7iVa1$VgHV0uUAYj0msJuL+CW/7/828vYrO/iBkuDVh18ljKI=	2020-10-15 16:48:43.973574+00	t	hyformadmin			hyformadmin@a.com	t	t	2020-10-15 16:48:12.167978+00
2	pbkdf2_sha256$150000$Uqqu524tCxYN$YHu1WJcplAUqHHONdQTIUgP4t5VzKDARlS8kpJsPX8w=	2020-10-15 16:55:27.676218+00	f	hyform-exper				f	t	2020-05-19 23:15:43+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.authtoken_token (key, created, user_id) FROM stdin;
1488637928985e96cfaa5f9e89b9bdd154ef0fa0	2020-10-15 16:46:07.914125+00	2
\.


--
-- Data for Name: chat_channel; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.chat_channel (id, name, structure_id) FROM stdin;
32	All	1
38	Help	\N
39	Setup	\N
40	Session	\N
37	Ops - Design 2	2
36	Ops - Design 1	2
35	Ops Mgr - Ops 2	2
34	Ops Mgr - Ops 1	2
33	Business - Ops Mgr	2
31	Business - Mgrs	1
30	Operations Team	1
29	Design Team	1
\.


--
-- Data for Name: chat_channelposition; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.chat_channelposition (id, channel_id, position_id) FROM stdin;
1	29	5
2	29	6
3	30	2
4	30	3
5	30	4
6	31	1
7	31	2
8	31	5
9	32	1
10	32	2
11	32	5
12	32	3
13	32	4
14	32	6
15	33	7
16	33	8
17	34	8
18	34	9
19	35	8
20	35	10
21	36	9
22	36	11
23	37	10
24	37	12
\.


--
-- Data for Name: chat_message; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.chat_message (id, message, "timestamp", channel_id, sender_id, session_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2020-10-15 16:49:10.713126+00	2	hyform-exper	2	[{"changed": {"fields": ["password"]}}]	4	15
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	authtoken	token
8	repo	address
9	repo	customer
10	repo	designteam
11	repo	opsplandemo
12	repo	path
13	repo	playdemo
14	repo	scenariodemo
15	repo	vehicledemo
16	repo	waypoint
17	repo	warehouse
18	repo	vehicle
19	repo	scenario
20	repo	plan
21	repo	datalog
22	repo	profile
23	repo	pathcustomer
24	repo	customerscenario
25	ai	designer1
26	chat	channel
27	chat	message
28	chat	channelposition
29	exper	experiment
30	exper	group
31	exper	market
32	exper	position
33	exper	role
34	exper	session
35	exper	structure
36	exper	study
37	exper	userposition
38	exper	sessionteam
39	exper	groupposition
40	exper	organization
41	exper	userchecklist
42	authtoken	tokenproxy
43	repo	experorg
44	exper	customlinks
45	exper	exercise
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2020-05-18 16:20:12.616613+00
2	auth	0001_initial	2020-05-18 16:20:12.672573+00
3	admin	0001_initial	2020-05-18 16:20:12.792529+00
4	admin	0002_logentry_remove_auto_add	2020-05-18 16:20:12.824674+00
5	admin	0003_logentry_add_action_flag_choices	2020-05-18 16:20:12.837288+00
6	ai	0001_initial	2020-05-18 16:20:12.849314+00
7	contenttypes	0002_remove_content_type_name	2020-05-18 16:20:12.874946+00
8	auth	0002_alter_permission_name_max_length	2020-05-18 16:20:12.884706+00
9	auth	0003_alter_user_email_max_length	2020-05-18 16:20:12.897221+00
10	auth	0004_alter_user_username_opts	2020-05-18 16:20:12.909994+00
11	auth	0005_alter_user_last_login_null	2020-05-18 16:20:12.922523+00
12	auth	0006_require_contenttypes_0002	2020-05-18 16:20:12.926844+00
13	auth	0007_alter_validators_add_error_messages	2020-05-18 16:20:12.938719+00
14	auth	0008_alter_user_username_max_length	2020-05-18 16:20:12.955941+00
15	auth	0009_alter_user_last_name_max_length	2020-05-18 16:20:12.970719+00
16	auth	0010_alter_group_name_max_length	2020-05-18 16:20:12.982199+00
17	auth	0011_update_proxy_permissions	2020-05-18 16:20:12.994851+00
18	authtoken	0001_initial	2020-05-18 16:20:13.010005+00
19	authtoken	0002_auto_20160226_1747	2020-05-18 16:20:13.060785+00
20	repo	0001_initial	2020-05-18 16:20:13.291379+00
21	repo	0002_datalog	2020-05-18 16:20:13.48108+00
22	repo	0003_vehicle_payload	2020-05-18 16:20:13.511434+00
23	repo	0004_profile	2020-05-18 16:20:13.543178+00
24	repo	0005_auto_20200206_1411	2020-05-18 16:20:13.596516+00
25	repo	0006_auto_20200210_1944	2020-05-18 16:20:13.621675+00
26	exper	0001_initial	2020-05-18 16:20:13.9538+00
27	exper	0002_study_lead	2020-05-18 16:20:14.066677+00
28	exper	0003_auto_20200214_1252	2020-05-18 16:20:14.111041+00
29	exper	0004_auto_20200214_1254	2020-05-18 16:20:14.155241+00
30	exper	0005_groupposition_primary	2020-05-18 16:20:14.174927+00
31	exper	0006_experiment_user	2020-05-18 16:20:14.207147+00
32	exper	0007_organization	2020-05-18 16:20:14.219266+00
33	exper	0008_userposition_session	2020-05-18 16:20:14.253014+00
34	exper	0009_auto_20200310_1958	2020-05-18 16:20:14.270194+00
35	chat	0001_initial	2020-05-18 16:20:14.34237+00
36	chat	0002_channel_team	2020-05-18 16:20:14.397585+00
37	chat	0003_auto_20200207_1824	2020-05-18 16:20:14.450381+00
38	chat	0004_auto_20200213_2048	2020-05-18 16:20:14.607087+00
39	chat	0005_auto_20200214_1225	2020-05-18 16:20:14.703376+00
40	chat	0006_message_session	2020-05-18 16:20:14.81945+00
41	chat	0007_auto_20200224_1935	2020-05-18 16:20:14.865753+00
42	chat	0008_auto_20200316_1753	2020-05-18 16:20:14.917077+00
43	exper	0010_userchecklist	2020-05-18 16:20:14.954624+00
44	repo	0007_auto_20200214_1514	2020-05-18 16:20:14.999621+00
45	repo	0008_auto_20200217_1800	2020-05-18 16:20:15.859185+00
46	repo	0009_auto_20200218_1253	2020-05-18 16:20:16.107232+00
47	repo	0010_auto_20200218_1340	2020-05-18 16:20:16.303142+00
48	repo	0011_scenario_cusomters	2020-05-18 16:20:16.367177+00
49	repo	0012_auto_20200219_1551	2020-05-18 16:20:16.567876+00
50	repo	0013_auto_20200219_1612	2020-05-18 16:20:16.602042+00
51	repo	0014_remove_scenario_customers	2020-05-18 16:20:16.645545+00
52	repo	0015_scenario_customers	2020-05-18 16:20:16.679112+00
53	repo	0016_remove_scenario_customers	2020-05-18 16:20:16.710495+00
54	repo	0017_profile_is_exper	2020-05-18 16:20:16.737791+00
55	repo	0018_auto_20200220_2022	2020-05-18 16:20:16.882246+00
56	repo	0019_pathcustomer_stop	2020-05-18 16:20:16.911895+00
57	repo	0020_auto_20200220_2215	2020-05-18 16:20:16.955793+00
58	repo	0021_auto_20200220_2218	2020-05-18 16:20:17.002408+00
59	repo	0022_auto_20200225_1511	2020-05-18 16:20:17.121456+00
60	repo	0023_auto_20200306_1430	2020-05-18 16:20:17.211921+00
61	repo	0024_datalog_type	2020-05-18 16:20:17.254838+00
62	repo	0025_auto_20200320_0348	2020-05-18 16:20:17.281404+00
63	repo	0026_profile_temp_code	2020-05-18 16:20:17.336986+00
64	repo	0027_auto_20200429_1430	2020-05-18 16:20:17.362017+00
65	sessions	0001_initial	2020-05-18 16:20:17.374813+00
66	auth	0012_alter_user_first_name_max_length	2020-10-15 14:45:22.407619+00
67	authtoken	0003_tokenproxy	2020-10-15 14:45:22.416377+00
68	exper	0011_customlinks	2020-10-15 14:45:22.456884+00
69	exper	0012_auto_20200608_1638	2020-10-15 14:45:22.627069+00
70	exper	0013_customlinks_structure	2020-10-15 14:45:22.66047+00
71	exper	0014_structure_organization	2020-10-15 14:45:22.694417+00
72	exper	0015_auto_20200907_1752	2020-10-15 14:45:22.89998+00
73	exper	0016_study_organization	2020-10-15 14:45:22.935554+00
74	exper	0017_auto_20200909_1000	2020-10-15 14:45:22.979167+00
75	exper	0018_auto_20200909_1002	2020-10-15 14:45:23.018023+00
76	exper	0019_auto_20200909_1005	2020-10-15 14:45:23.057775+00
77	exper	0020_auto_20200909_1353	2020-10-15 14:45:23.069153+00
78	repo	0028_profile_user_type	2020-10-15 14:45:23.090598+00
79	repo	0029_auto_20200909_0127	2020-10-15 14:45:23.156679+00
80	repo	0030_experorg	2020-10-15 14:45:23.194747+00
81	repo	0027_remove_profile_temp_code	2020-10-15 14:45:23.222579+00
82	repo	0028_profile_temp_code	2020-10-15 14:45:23.24527+00
83	repo	0029_merge_20200501_1418	2020-10-15 14:45:23.247895+00
84	repo	0031_merge_20200909_2122	2020-10-15 14:45:23.250631+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
to9pyu446tkmonc8wrqx9kiaczjynsln	YTg0NTM2N2U1NjE2NGQ5NmZmMzdiODQzZjVlYWFjZjZmMWQyNDM0Njp7Il9hdXRoX3VzZXJfaWQiOiIyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI5MGZjOTg0YzY2YTIxNjM2OTgzOWM0MDk1Njc1MzIxYzQzYTQ2MmMzIn0=	2020-10-29 16:55:27.680834+00
\.


--
-- Data for Name: exper_customlinks; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_customlinks (id, text, link, link_type, is_team, ai, status, first, last, org_id, position_id, role_id, structure_id) FROM stdin;
\.


--
-- Data for Name: exper_exercise; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_exercise (id, name, experiment_id) FROM stdin;
\.


--
-- Data for Name: exper_experiment; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_experiment (id, name, study_id, user_id) FROM stdin;
1	Hyform Experiment	1	2
\.


--
-- Data for Name: exper_group; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_group (id, name, structure_id) FROM stdin;
10	All	1
11	All	2
12	Subteam 1	2
13	Subteam 2	2
14	Design 1	3
15	Design 2	3
16	Design 3	3
17	Design 4	3
18	All	3
19	Design 5	3
20	Design 6	3
\.


--
-- Data for Name: exper_groupposition; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_groupposition (id, group_id, position_id, "primary") FROM stdin;
35	11	9	f
36	11	10	f
37	11	11	f
38	11	12	f
39	12	8	f
42	13	8	f
32	10	6	t
31	10	5	t
30	10	4	t
29	10	3	t
28	10	2	t
27	10	1	t
44	13	12	t
43	13	10	t
41	12	11	t
40	12	9	t
34	11	8	t
33	11	7	t
45	12	7	f
46	13	7	f
47	14	13	t
48	15	14	t
49	16	15	t
50	17	16	t
51	18	13	f
52	18	14	f
53	18	15	f
54	18	16	f
55	19	17	t
56	20	18	t
57	18	17	f
58	18	18	f
\.


--
-- Data for Name: exper_market; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_market (id, name) FROM stdin;
1	Market 1
2	Market 2
\.


--
-- Data for Name: exper_organization; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_organization (id, name) FROM stdin;
1	HyForm
\.


--
-- Data for Name: exper_position; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_position (id, name, role_id, structure_id) FROM stdin;
1	Business	3	1
2	Operations Manager	2	1
3	Operations Specialist 1	2	1
4	Operations Specialist 2	2	1
5	Design Manager	1	1
6	Design Specialist	1	1
7	Business	3	2
8	Operations Manager	2	2
9	Operations Specialist 1	2	2
10	Operations Specialist 2	2	2
11	Design Specialist 1	1	2
12	Design Specialist 2	1	2
13	Design Specialist 1	1	3
14	Design Specialist 2	1	3
15	Design Specialist 3	1	3
16	Design Specialist 4	1	3
17	Design Specialist 5	1	3
18	Design Specialist 6	1	3
\.


--
-- Data for Name: exper_role; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_role (id, name) FROM stdin;
1	Designer
3	Business
2	OpsPlanner
\.


--
-- Data for Name: exper_session; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_session (id, name, use_ai, status, experiment_id, market_id, prior_session_id, structure_id, index, exercise_id) FROM stdin;
\.


--
-- Data for Name: exper_sessionteam; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_sessionteam (id, session_id, team_id) FROM stdin;
\.


--
-- Data for Name: exper_structure; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_structure (id, name, organization_id) FROM stdin;
1	A	\N
2	B	\N
3	Extra	\N
\.


--
-- Data for Name: exper_study; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_study (id, name, purpose, lead, organization_id) FROM stdin;
1	HyForm Study	Basic study	no one	\N
\.


--
-- Data for Name: exper_userchecklist; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_userchecklist (id, precheck, postcheck, session_id, user_id) FROM stdin;
\.


--
-- Data for Name: exper_userposition; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.exper_userposition (id, position_id, user_id, session_id) FROM stdin;
\.


--
-- Data for Name: repo_address; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_address (id, x, z, region) FROM stdin;
113	-3.5	0	warehouse
112	-0.8	6.4	r
111	-0.7	7.2	r
110	-1.7	5.3	r
109	-2.8	6.2	r
108	-2.2	7	r
107	-0.2	5.8	r
106	-3	5.1	r
105	-1.5	6.9	r
104	-2.1	6	r
103	-1	5.6	r
102	6.9	-0.8	r
101	6.5	-1	r
100	2	3.1	r
99	-4.5	-6	r
98	-6.5	-6.8	r
97	-7.2	5.5	r
96	-5.3	2.4	r
95	-6.5	0.4	r
94	-6.1	1.3	r
93	-6.6	2.4	r
92	-6.5	3.4	r
91	-4.6	1.9	r
90	-5.8	3	r
89	-5.2	1.2	r
88	-7.4	1.4	r
87	-6	2	r
86	-2.4	-3.7	r
85	-3.1	-4.4	r
84	-1.7	-3.4	r
83	-1	-4.8	r
82	-3.2	-3.6	r
81	-1.7	-4.4	r
80	-1	-5.6	r
79	-3.8	-3.8	r
78	-2	-5.1	r
77	-1.2	-4	r
76	0.6	1	r
75	0.7	0.3	r
74	-0.8	-1.6	r
73	0.4	-0.8	r
72	-0.3	-0.4	r
71	-0.6	0.2	r
70	-1.4	-1.2	r
69	1	-0.5	r
68	-0.7	1.2	r
67	0.1	0.6	r
66	2.1	-6.4	r
65	1.5	-5.9	r
64	1.1	-6.3	r
63	2.2	-5.6	r
62	2.8	-6	r
61	6	5.1	r
60	6.8	5.3	r
59	7.4	4.8	r
58	6.5	4.7	r
57	7.4	5.7	r
\.


--
-- Data for Name: repo_customer; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_customer (id, market_id, payload, weight, address_id) FROM stdin;
57	1	package	4	57
58	1	package	3	58
59	1	package	3	59
60	1	package	4	60
61	1	package	3	61
62	1	package	1	62
63	1	package	1	63
64	1	package	4	64
65	1	package	1	65
66	1	package	4	66
67	1	package	2	67
68	1	package	2	68
69	1	package	2	69
70	1	package	3	70
71	1	package	2	71
72	1	package	1	72
73	1	package	3	73
74	1	package	2	74
75	1	package	2	75
76	1	package	1	76
77	1	package	1	77
78	1	package	3	78
79	1	package	1	79
80	1	package	4	80
81	1	package	2	81
82	1	package	1	82
83	1	package	3	83
84	1	package	2	84
85	1	package	3	85
86	1	package	4	86
87	1	package	3	87
88	1	package	1	88
89	1	package	3	89
90	1	package	2	90
91	1	package	3	91
92	1	package	4	92
93	1	package	4	93
94	1	package	2	94
95	1	package	1	95
96	1	package	4	96
97	1	package	2	97
98	1	package	4	98
99	1	package	3	99
100	1	package	3	100
101	1	package	3	101
102	1	package	1	102
103	1	food2	2	103
104	1	food2	2	104
105	1	food2	1	105
106	1	food2	2	106
107	1	food2	1	107
108	1	food2	1	108
109	1	food2	1	109
110	1	food2	2	110
111	1	food2	1	111
112	1	food2	1	112
113	2	food2	2	112
114	2	food2	4	111
115	2	food2	2	110
116	2	food2	3	109
117	2	food2	4	108
118	2	food2	4	107
119	2	food2	4	106
120	2	food2	3	105
121	2	food2	2	104
122	2	food2	2	103
123	2	food2	2	102
124	2	food2	3	101
125	2	food2	7	100
126	2	food2	3	99
127	2	food2	6	98
128	2	food2	3	97
129	2	package	4	96
130	2	package	1	95
131	2	package	2	94
132	2	package	4	93
133	2	package	4	92
134	2	package	3	91
135	2	food2	2	90
136	2	food2	4	89
137	2	food2	4	88
138	2	food2	3	87
139	2	food2	4	86
140	2	package	3	85
141	2	package	2	84
142	2	package	3	83
143	2	package	1	82
144	2	food2	4	81
145	2	package	4	80
146	2	food2	6	79
147	2	food2	3	78
148	2	food2	1	77
149	2	package	1	76
150	2	food2	2	75
151	2	package	2	74
152	2	food2	4	73
153	2	package	2	72
154	2	package	2	71
155	2	food2	4	70
156	2	food2	3	69
157	2	food2	4	68
158	2	package	2	67
159	2	food2	4	66
160	2	food2	3	65
161	2	food2	2	64
162	2	package	4	63
163	2	food2	2	62
164	2	food2	3	61
165	2	food2	4	60
166	2	food2	3	59
167	2	package	3	58
168	2	food2	7	57
\.


--
-- Data for Name: repo_customerscenario; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_customerscenario (id, selected, customer_id, scenario_id) FROM stdin;
\.


--
-- Data for Name: repo_datalog; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_datalog (id, user_id, "time", action, session_id, type) FROM stdin;
\.


--
-- Data for Name: repo_designteam; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_designteam (id, name, initialscore, currentscore, organization_id) FROM stdin;
1	Hyform Team 1	0	0	1
2	Hyform Team 2	0	0	1
\.


--
-- Data for Name: repo_experorg; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_experorg (id, organization_id, user_id) FROM stdin;
\.


--
-- Data for Name: repo_opsplandemo; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_opsplandemo (id, xmlstring, tag, team) FROM stdin;
\.


--
-- Data for Name: repo_path; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_path (id, leavetime, returntime, vehicle_id, warehouse_id, group_id, session_id, plan_id) FROM stdin;
\.


--
-- Data for Name: repo_pathcustomer; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_pathcustomer (id, customer_id, path_id, stop) FROM stdin;
\.


--
-- Data for Name: repo_plan; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_plan (id, tag, scenario_id, group_id, session_id) FROM stdin;
\.


--
-- Data for Name: repo_playdemo; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_playdemo (id, xmlstring, tag, team) FROM stdin;
\.


--
-- Data for Name: repo_profile; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_profile (id, team_id, user_id, is_exper, organization_id, user_type, experiment_id, study_id, temp_code) FROM stdin;
3	1	3	f	\N	1	\N	\N	
4	1	4	f	\N	1	\N	\N	
5	1	5	f	\N	1	\N	\N	
6	1	6	f	\N	1	\N	\N	
7	1	7	f	\N	1	\N	\N	
8	1	8	f	\N	1	\N	\N	
9	2	9	f	\N	1	\N	\N	
10	2	10	f	\N	1	\N	\N	
11	2	11	f	\N	1	\N	\N	
12	2	12	f	\N	1	\N	\N	
13	2	13	f	\N	1	\N	\N	
14	2	14	f	\N	1	\N	\N	
15	\N	15	f	\N	1	\N	\N	
2	\N	2	t	1	2	\N	\N	
\.


--
-- Data for Name: repo_scenario; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_scenario (id, tag, warehouse_id, group_id, session_id, version) FROM stdin;
\.


--
-- Data for Name: repo_scenariodemo; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_scenariodemo (id, xmlstring, tag, team) FROM stdin;
\.


--
-- Data for Name: repo_vehicle; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_vehicle (id, tag, config, result, range, velocity, cost, payload, group_id, session_id) FROM stdin;
\.


--
-- Data for Name: repo_vehicledemo; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_vehicledemo (id, xmlstring, tag, team) FROM stdin;
\.


--
-- Data for Name: repo_warehouse; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_warehouse (id, address_id, group_id, session_id) FROM stdin;
\.


--
-- Data for Name: repo_waypoint; Type: TABLE DATA; Schema: public; Owner: atuser
--

COPY public.repo_waypoint (id, deliverytime, customer_id) FROM stdin;
\.


--
-- Name: ai_designer1_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.ai_designer1_id_seq', 13214, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 180, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 15, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: chat_channel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.chat_channel_id_seq', 40, true);


--
-- Name: chat_channelposition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.chat_channelposition_id_seq', 24, true);


--
-- Name: chat_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.chat_message_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 45, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 84, true);


--
-- Name: exper_customlinks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_customlinks_id_seq', 1, false);


--
-- Name: exper_exercise_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_exercise_id_seq', 1, false);


--
-- Name: exper_experiment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_experiment_id_seq', 1, true);


--
-- Name: exper_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_group_id_seq', 23, true);


--
-- Name: exper_groupposition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_groupposition_id_seq', 68, true);


--
-- Name: exper_market_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_market_id_seq', 2, true);


--
-- Name: exper_organization_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_organization_id_seq', 1, true);


--
-- Name: exper_position_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_position_id_seq', 18, true);


--
-- Name: exper_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_role_id_seq', 4, true);


--
-- Name: exper_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_session_id_seq', 1, false);


--
-- Name: exper_sessionteam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_sessionteam_id_seq', 1, false);


--
-- Name: exper_structure_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_structure_id_seq', 3, true);


--
-- Name: exper_study_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_study_id_seq', 1, true);


--
-- Name: exper_userchecklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_userchecklist_id_seq', 1, false);


--
-- Name: exper_userposition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.exper_userposition_id_seq', 1, false);


--
-- Name: repo_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_address_id_seq', 113, true);


--
-- Name: repo_customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_customer_id_seq', 168, true);


--
-- Name: repo_customerlist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_customerlist_id_seq', 1, false);


--
-- Name: repo_datalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_datalog_id_seq', 1, false);


--
-- Name: repo_designteam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_designteam_id_seq', 2, true);


--
-- Name: repo_experorg_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_experorg_id_seq', 1, false);


--
-- Name: repo_opsplandemo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_opsplandemo_id_seq', 1, false);


--
-- Name: repo_path_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_path_id_seq', 1, false);


--
-- Name: repo_pathcustomer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_pathcustomer_id_seq', 1, false);


--
-- Name: repo_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_plan_id_seq', 1, false);


--
-- Name: repo_playdemo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_playdemo_id_seq', 1, false);


--
-- Name: repo_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_profile_id_seq', 15, true);


--
-- Name: repo_scenario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_scenario_id_seq', 1, false);


--
-- Name: repo_scenariodemo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_scenariodemo_id_seq', 1, false);


--
-- Name: repo_vehicle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_vehicle_id_seq', 1, false);


--
-- Name: repo_vehicledemo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_vehicledemo_id_seq', 1, false);


--
-- Name: repo_warehouse_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_warehouse_id_seq', 1, false);


--
-- Name: repo_waypoint_id_seq; Type: SEQUENCE SET; Schema: public; Owner: atuser
--

SELECT pg_catalog.setval('public.repo_waypoint_id_seq', 1, false);


--
-- Name: ai_designer1 ai_designer1_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.ai_designer1
    ADD CONSTRAINT ai_designer1_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: authtoken_token authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: chat_channel chat_channel_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channel
    ADD CONSTRAINT chat_channel_pkey PRIMARY KEY (id);


--
-- Name: chat_channelposition chat_channelposition_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channelposition
    ADD CONSTRAINT chat_channelposition_pkey PRIMARY KEY (id);


--
-- Name: chat_message chat_message_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: exper_customlinks exper_customlinks_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks
    ADD CONSTRAINT exper_customlinks_pkey PRIMARY KEY (id);


--
-- Name: exper_exercise exper_exercise_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_exercise
    ADD CONSTRAINT exper_exercise_pkey PRIMARY KEY (id);


--
-- Name: exper_experiment exper_experiment_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_experiment
    ADD CONSTRAINT exper_experiment_pkey PRIMARY KEY (id);


--
-- Name: exper_group exper_group_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_group
    ADD CONSTRAINT exper_group_pkey PRIMARY KEY (id);


--
-- Name: exper_groupposition exper_groupposition_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_groupposition
    ADD CONSTRAINT exper_groupposition_pkey PRIMARY KEY (id);


--
-- Name: exper_market exper_market_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_market
    ADD CONSTRAINT exper_market_pkey PRIMARY KEY (id);


--
-- Name: exper_organization exper_organization_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_organization
    ADD CONSTRAINT exper_organization_pkey PRIMARY KEY (id);


--
-- Name: exper_position exper_position_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_position
    ADD CONSTRAINT exper_position_pkey PRIMARY KEY (id);


--
-- Name: exper_role exper_role_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_role
    ADD CONSTRAINT exper_role_pkey PRIMARY KEY (id);


--
-- Name: exper_session exper_session_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_pkey PRIMARY KEY (id);


--
-- Name: exper_sessionteam exper_sessionteam_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_sessionteam
    ADD CONSTRAINT exper_sessionteam_pkey PRIMARY KEY (id);


--
-- Name: exper_structure exper_structure_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_structure
    ADD CONSTRAINT exper_structure_pkey PRIMARY KEY (id);


--
-- Name: exper_study exper_study_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_study
    ADD CONSTRAINT exper_study_pkey PRIMARY KEY (id);


--
-- Name: exper_userchecklist exper_userchecklist_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userchecklist
    ADD CONSTRAINT exper_userchecklist_pkey PRIMARY KEY (id);


--
-- Name: exper_userposition exper_userposition_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userposition
    ADD CONSTRAINT exper_userposition_pkey PRIMARY KEY (id);


--
-- Name: repo_address repo_address_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_address
    ADD CONSTRAINT repo_address_pkey PRIMARY KEY (id);


--
-- Name: repo_customer repo_customer_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customer
    ADD CONSTRAINT repo_customer_pkey PRIMARY KEY (id);


--
-- Name: repo_customerscenario repo_customerlist_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customerscenario
    ADD CONSTRAINT repo_customerlist_pkey PRIMARY KEY (id);


--
-- Name: repo_datalog repo_datalog_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_datalog
    ADD CONSTRAINT repo_datalog_pkey PRIMARY KEY (id);


--
-- Name: repo_designteam repo_designteam_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_designteam
    ADD CONSTRAINT repo_designteam_pkey PRIMARY KEY (id);


--
-- Name: repo_experorg repo_experorg_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_experorg
    ADD CONSTRAINT repo_experorg_pkey PRIMARY KEY (id);


--
-- Name: repo_opsplandemo repo_opsplandemo_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_opsplandemo
    ADD CONSTRAINT repo_opsplandemo_pkey PRIMARY KEY (id);


--
-- Name: repo_path repo_path_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_pkey PRIMARY KEY (id);


--
-- Name: repo_pathcustomer repo_pathcustomer_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_pathcustomer
    ADD CONSTRAINT repo_pathcustomer_pkey PRIMARY KEY (id);


--
-- Name: repo_plan repo_plan_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_plan
    ADD CONSTRAINT repo_plan_pkey PRIMARY KEY (id);


--
-- Name: repo_playdemo repo_playdemo_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_playdemo
    ADD CONSTRAINT repo_playdemo_pkey PRIMARY KEY (id);


--
-- Name: repo_profile repo_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_pkey PRIMARY KEY (id);


--
-- Name: repo_profile repo_profile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_user_id_key UNIQUE (user_id);


--
-- Name: repo_scenario repo_scenario_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenario
    ADD CONSTRAINT repo_scenario_pkey PRIMARY KEY (id);


--
-- Name: repo_scenariodemo repo_scenariodemo_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenariodemo
    ADD CONSTRAINT repo_scenariodemo_pkey PRIMARY KEY (id);


--
-- Name: repo_vehicle repo_vehicle_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicle
    ADD CONSTRAINT repo_vehicle_pkey PRIMARY KEY (id);


--
-- Name: repo_vehicledemo repo_vehicledemo_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicledemo
    ADD CONSTRAINT repo_vehicledemo_pkey PRIMARY KEY (id);


--
-- Name: repo_warehouse repo_warehouse_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_warehouse
    ADD CONSTRAINT repo_warehouse_pkey PRIMARY KEY (id);


--
-- Name: repo_waypoint repo_waypoint_pkey; Type: CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_waypoint
    ADD CONSTRAINT repo_waypoint_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: authtoken_token_key_10f0b77e_like; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX authtoken_token_key_10f0b77e_like ON public.authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: chat_channel_structure_id_88650d98; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_channel_structure_id_88650d98 ON public.chat_channel USING btree (structure_id);


--
-- Name: chat_channelposition_channel_id_caa65fa1; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_channelposition_channel_id_caa65fa1 ON public.chat_channelposition USING btree (channel_id);


--
-- Name: chat_channelposition_position_id_ba44c786; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_channelposition_position_id_ba44c786 ON public.chat_channelposition USING btree (position_id);


--
-- Name: chat_message_channel_id_62858528; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_message_channel_id_62858528 ON public.chat_message USING btree (channel_id);


--
-- Name: chat_message_sender_id_991c686c; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_message_sender_id_991c686c ON public.chat_message USING btree (sender_id);


--
-- Name: chat_message_session_id_9abc6edf; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX chat_message_session_id_9abc6edf ON public.chat_message USING btree (session_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: exper_customlinks_org_id_58d58a88; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_customlinks_org_id_58d58a88 ON public.exper_customlinks USING btree (org_id);


--
-- Name: exper_customlinks_position_id_fb3005c9; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_customlinks_position_id_fb3005c9 ON public.exper_customlinks USING btree (position_id);


--
-- Name: exper_customlinks_role_id_30317a0f; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_customlinks_role_id_30317a0f ON public.exper_customlinks USING btree (role_id);


--
-- Name: exper_customlinks_structure_id_127430c8; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_customlinks_structure_id_127430c8 ON public.exper_customlinks USING btree (structure_id);


--
-- Name: exper_exercise_experiment_id_99e8b40b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_exercise_experiment_id_99e8b40b ON public.exper_exercise USING btree (experiment_id);


--
-- Name: exper_experiment_study_id_4a34eeef; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_experiment_study_id_4a34eeef ON public.exper_experiment USING btree (study_id);


--
-- Name: exper_experiment_user_id_37955031; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_experiment_user_id_37955031 ON public.exper_experiment USING btree (user_id);


--
-- Name: exper_group_structure_id_499ae147; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_group_structure_id_499ae147 ON public.exper_group USING btree (structure_id);


--
-- Name: exper_groupposition_group_id_8383bc68; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_groupposition_group_id_8383bc68 ON public.exper_groupposition USING btree (group_id);


--
-- Name: exper_groupposition_position_id_3701a4ea; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_groupposition_position_id_3701a4ea ON public.exper_groupposition USING btree (position_id);


--
-- Name: exper_position_role_id_8bb863bc; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_position_role_id_8bb863bc ON public.exper_position USING btree (role_id);


--
-- Name: exper_position_structure_id_63052ff5; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_position_structure_id_63052ff5 ON public.exper_position USING btree (structure_id);


--
-- Name: exper_session_exercise_id_963529d1; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_session_exercise_id_963529d1 ON public.exper_session USING btree (exercise_id);


--
-- Name: exper_session_experiment_id_fe5ee374; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_session_experiment_id_fe5ee374 ON public.exper_session USING btree (experiment_id);


--
-- Name: exper_session_market_id_5fb0f03b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_session_market_id_5fb0f03b ON public.exper_session USING btree (market_id);


--
-- Name: exper_session_prior_session_id_47014bc3; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_session_prior_session_id_47014bc3 ON public.exper_session USING btree (prior_session_id);


--
-- Name: exper_session_structure_id_151e905b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_session_structure_id_151e905b ON public.exper_session USING btree (structure_id);


--
-- Name: exper_sessionteam_session_id_b0c33f4c; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_sessionteam_session_id_b0c33f4c ON public.exper_sessionteam USING btree (session_id);


--
-- Name: exper_sessionteam_team_id_b2f4d6fc; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_sessionteam_team_id_b2f4d6fc ON public.exper_sessionteam USING btree (team_id);


--
-- Name: exper_structure_organization_id_8e76cbfc; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_structure_organization_id_8e76cbfc ON public.exper_structure USING btree (organization_id);


--
-- Name: exper_study_organization_id_a3359eee; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_study_organization_id_a3359eee ON public.exper_study USING btree (organization_id);


--
-- Name: exper_userchecklist_session_id_7af56823; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_userchecklist_session_id_7af56823 ON public.exper_userchecklist USING btree (session_id);


--
-- Name: exper_userchecklist_user_id_8398564e; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_userchecklist_user_id_8398564e ON public.exper_userchecklist USING btree (user_id);


--
-- Name: exper_userposition_position_id_72255e27; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_userposition_position_id_72255e27 ON public.exper_userposition USING btree (position_id);


--
-- Name: exper_userposition_session_id_e3188377; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_userposition_session_id_e3188377 ON public.exper_userposition USING btree (session_id);


--
-- Name: exper_userposition_user_id_5f752b9c; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX exper_userposition_user_id_5f752b9c ON public.exper_userposition USING btree (user_id);


--
-- Name: repo_customer_address_id_8707cfeb; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_customer_address_id_8707cfeb ON public.repo_customer USING btree (address_id);


--
-- Name: repo_customer_market_id_90025ff2; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_customer_market_id_90025ff2 ON public.repo_customer USING btree (market_id);


--
-- Name: repo_customerlist_customer_id_7907e817; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_customerlist_customer_id_7907e817 ON public.repo_customerscenario USING btree (customer_id);


--
-- Name: repo_customerlist_scenario_id_ed9698c1; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_customerlist_scenario_id_ed9698c1 ON public.repo_customerscenario USING btree (scenario_id);


--
-- Name: repo_datalog_session_id_7a8d696e; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_datalog_session_id_7a8d696e ON public.repo_datalog USING btree (session_id);


--
-- Name: repo_datalog_user_id_03f53ea0; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_datalog_user_id_03f53ea0 ON public.repo_datalog USING btree (user_id);


--
-- Name: repo_designteam_organization_id_2ce2d1f4; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_designteam_organization_id_2ce2d1f4 ON public.repo_designteam USING btree (organization_id);


--
-- Name: repo_experorg_organization_id_878492eb; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_experorg_organization_id_878492eb ON public.repo_experorg USING btree (organization_id);


--
-- Name: repo_experorg_user_id_3b7e2f80; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_experorg_user_id_3b7e2f80 ON public.repo_experorg USING btree (user_id);


--
-- Name: repo_path_group_id_4c6d38a9; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_path_group_id_4c6d38a9 ON public.repo_path USING btree (group_id);


--
-- Name: repo_path_plan_id_c1df2ac7; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_path_plan_id_c1df2ac7 ON public.repo_path USING btree (plan_id);


--
-- Name: repo_path_session_id_de064431; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_path_session_id_de064431 ON public.repo_path USING btree (session_id);


--
-- Name: repo_path_vehicle_id_4fe4e49b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_path_vehicle_id_4fe4e49b ON public.repo_path USING btree (vehicle_id);


--
-- Name: repo_path_warehouse_id_109b6550; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_path_warehouse_id_109b6550 ON public.repo_path USING btree (warehouse_id);


--
-- Name: repo_pathcustomer_customer_id_54cd0293; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_pathcustomer_customer_id_54cd0293 ON public.repo_pathcustomer USING btree (customer_id);


--
-- Name: repo_pathcustomer_path_id_b2678cab; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_pathcustomer_path_id_b2678cab ON public.repo_pathcustomer USING btree (path_id);


--
-- Name: repo_plan_group_id_e54fe137; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_plan_group_id_e54fe137 ON public.repo_plan USING btree (group_id);


--
-- Name: repo_plan_scenario_id_cba976c5; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_plan_scenario_id_cba976c5 ON public.repo_plan USING btree (scenario_id);


--
-- Name: repo_plan_session_id_a9eb4fda; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_plan_session_id_a9eb4fda ON public.repo_plan USING btree (session_id);


--
-- Name: repo_profile_experiment_id_d7a90e91; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_profile_experiment_id_d7a90e91 ON public.repo_profile USING btree (experiment_id);


--
-- Name: repo_profile_organization_id_514cb12b; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_profile_organization_id_514cb12b ON public.repo_profile USING btree (organization_id);


--
-- Name: repo_profile_study_id_2228ba08; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_profile_study_id_2228ba08 ON public.repo_profile USING btree (study_id);


--
-- Name: repo_profile_team_id_0282cd4d; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_profile_team_id_0282cd4d ON public.repo_profile USING btree (team_id);


--
-- Name: repo_scenario_group_id_25f9c2b8; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_scenario_group_id_25f9c2b8 ON public.repo_scenario USING btree (group_id);


--
-- Name: repo_scenario_session_id_8a878579; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_scenario_session_id_8a878579 ON public.repo_scenario USING btree (session_id);


--
-- Name: repo_scenario_warehouse_id_bfa3234e; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_scenario_warehouse_id_bfa3234e ON public.repo_scenario USING btree (warehouse_id);


--
-- Name: repo_vehicle_group_id_efd51b25; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_vehicle_group_id_efd51b25 ON public.repo_vehicle USING btree (group_id);


--
-- Name: repo_vehicle_session_id_56e343f8; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_vehicle_session_id_56e343f8 ON public.repo_vehicle USING btree (session_id);


--
-- Name: repo_warehouse_address_id_a75a4f25; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_warehouse_address_id_a75a4f25 ON public.repo_warehouse USING btree (address_id);


--
-- Name: repo_warehouse_group_id_433c98d8; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_warehouse_group_id_433c98d8 ON public.repo_warehouse USING btree (group_id);


--
-- Name: repo_warehouse_session_id_f97e0bfc; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_warehouse_session_id_f97e0bfc ON public.repo_warehouse USING btree (session_id);


--
-- Name: repo_waypoint_customer_id_ab01026c; Type: INDEX; Schema: public; Owner: atuser
--

CREATE INDEX repo_waypoint_customer_id_ab01026c ON public.repo_waypoint USING btree (customer_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token authtoken_token_user_id_35299eff_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_channel chat_channel_structure_id_88650d98_fk_exper_structure_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channel
    ADD CONSTRAINT chat_channel_structure_id_88650d98_fk_exper_structure_id FOREIGN KEY (structure_id) REFERENCES public.exper_structure(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_channelposition chat_channelposition_channel_id_caa65fa1_fk_chat_channel_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channelposition
    ADD CONSTRAINT chat_channelposition_channel_id_caa65fa1_fk_chat_channel_id FOREIGN KEY (channel_id) REFERENCES public.chat_channel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_channelposition chat_channelposition_position_id_ba44c786_fk_exper_position_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_channelposition
    ADD CONSTRAINT chat_channelposition_position_id_ba44c786_fk_exper_position_id FOREIGN KEY (position_id) REFERENCES public.exper_position(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_message chat_message_channel_id_62858528_fk_chat_channel_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_channel_id_62858528_fk_chat_channel_id FOREIGN KEY (channel_id) REFERENCES public.chat_channel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_message chat_message_sender_id_991c686c_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_sender_id_991c686c_fk_auth_user_id FOREIGN KEY (sender_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: chat_message chat_message_session_id_9abc6edf_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.chat_message
    ADD CONSTRAINT chat_message_session_id_9abc6edf_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_customlinks exper_customlinks_org_id_58d58a88_fk_exper_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks
    ADD CONSTRAINT exper_customlinks_org_id_58d58a88_fk_exper_organization_id FOREIGN KEY (org_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_customlinks exper_customlinks_position_id_fb3005c9_fk_exper_position_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks
    ADD CONSTRAINT exper_customlinks_position_id_fb3005c9_fk_exper_position_id FOREIGN KEY (position_id) REFERENCES public.exper_position(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_customlinks exper_customlinks_role_id_30317a0f_fk_exper_role_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks
    ADD CONSTRAINT exper_customlinks_role_id_30317a0f_fk_exper_role_id FOREIGN KEY (role_id) REFERENCES public.exper_role(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_customlinks exper_customlinks_structure_id_127430c8_fk_exper_structure_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_customlinks
    ADD CONSTRAINT exper_customlinks_structure_id_127430c8_fk_exper_structure_id FOREIGN KEY (structure_id) REFERENCES public.exper_structure(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_exercise exper_exercise_experiment_id_99e8b40b_fk_exper_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_exercise
    ADD CONSTRAINT exper_exercise_experiment_id_99e8b40b_fk_exper_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.exper_experiment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_experiment exper_experiment_study_id_4a34eeef_fk_exper_study_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_experiment
    ADD CONSTRAINT exper_experiment_study_id_4a34eeef_fk_exper_study_id FOREIGN KEY (study_id) REFERENCES public.exper_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_experiment exper_experiment_user_id_37955031_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_experiment
    ADD CONSTRAINT exper_experiment_user_id_37955031_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_group exper_group_structure_id_499ae147_fk_exper_structure_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_group
    ADD CONSTRAINT exper_group_structure_id_499ae147_fk_exper_structure_id FOREIGN KEY (structure_id) REFERENCES public.exper_structure(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_groupposition exper_groupposition_group_id_8383bc68_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_groupposition
    ADD CONSTRAINT exper_groupposition_group_id_8383bc68_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_groupposition exper_groupposition_position_id_3701a4ea_fk_exper_position_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_groupposition
    ADD CONSTRAINT exper_groupposition_position_id_3701a4ea_fk_exper_position_id FOREIGN KEY (position_id) REFERENCES public.exper_position(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_position exper_position_role_id_8bb863bc_fk_exper_role_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_position
    ADD CONSTRAINT exper_position_role_id_8bb863bc_fk_exper_role_id FOREIGN KEY (role_id) REFERENCES public.exper_role(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_position exper_position_structure_id_63052ff5_fk_exper_structure_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_position
    ADD CONSTRAINT exper_position_structure_id_63052ff5_fk_exper_structure_id FOREIGN KEY (structure_id) REFERENCES public.exper_structure(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_session exper_session_exercise_id_963529d1_fk_exper_exercise_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_exercise_id_963529d1_fk_exper_exercise_id FOREIGN KEY (exercise_id) REFERENCES public.exper_exercise(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_session exper_session_experiment_id_fe5ee374_fk_exper_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_experiment_id_fe5ee374_fk_exper_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.exper_experiment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_session exper_session_market_id_5fb0f03b_fk_exper_market_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_market_id_5fb0f03b_fk_exper_market_id FOREIGN KEY (market_id) REFERENCES public.exper_market(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_session exper_session_prior_session_id_47014bc3_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_prior_session_id_47014bc3_fk_exper_session_id FOREIGN KEY (prior_session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_session exper_session_structure_id_151e905b_fk_exper_structure_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_session
    ADD CONSTRAINT exper_session_structure_id_151e905b_fk_exper_structure_id FOREIGN KEY (structure_id) REFERENCES public.exper_structure(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_sessionteam exper_sessionteam_session_id_b0c33f4c_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_sessionteam
    ADD CONSTRAINT exper_sessionteam_session_id_b0c33f4c_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_sessionteam exper_sessionteam_team_id_b2f4d6fc_fk_repo_designteam_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_sessionteam
    ADD CONSTRAINT exper_sessionteam_team_id_b2f4d6fc_fk_repo_designteam_id FOREIGN KEY (team_id) REFERENCES public.repo_designteam(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_structure exper_structure_organization_id_8e76cbfc_fk_exper_org; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_structure
    ADD CONSTRAINT exper_structure_organization_id_8e76cbfc_fk_exper_org FOREIGN KEY (organization_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_study exper_study_organization_id_a3359eee_fk_exper_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_study
    ADD CONSTRAINT exper_study_organization_id_a3359eee_fk_exper_organization_id FOREIGN KEY (organization_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_userchecklist exper_userchecklist_session_id_7af56823_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userchecklist
    ADD CONSTRAINT exper_userchecklist_session_id_7af56823_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_userchecklist exper_userchecklist_user_id_8398564e_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userchecklist
    ADD CONSTRAINT exper_userchecklist_user_id_8398564e_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_userposition exper_userposition_position_id_72255e27_fk_exper_position_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userposition
    ADD CONSTRAINT exper_userposition_position_id_72255e27_fk_exper_position_id FOREIGN KEY (position_id) REFERENCES public.exper_position(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_userposition exper_userposition_session_id_e3188377_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userposition
    ADD CONSTRAINT exper_userposition_session_id_e3188377_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exper_userposition exper_userposition_user_id_5f752b9c_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.exper_userposition
    ADD CONSTRAINT exper_userposition_user_id_5f752b9c_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_customer repo_customer_address_id_8707cfeb_fk_repo_address_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customer
    ADD CONSTRAINT repo_customer_address_id_8707cfeb_fk_repo_address_id FOREIGN KEY (address_id) REFERENCES public.repo_address(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_customer repo_customer_market_id_90025ff2_fk_exper_market_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customer
    ADD CONSTRAINT repo_customer_market_id_90025ff2_fk_exper_market_id FOREIGN KEY (market_id) REFERENCES public.exper_market(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_customerscenario repo_customerlist_customer_id_7907e817_fk_repo_customer_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customerscenario
    ADD CONSTRAINT repo_customerlist_customer_id_7907e817_fk_repo_customer_id FOREIGN KEY (customer_id) REFERENCES public.repo_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_customerscenario repo_customerlist_scenario_id_ed9698c1_fk_repo_scenario_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_customerscenario
    ADD CONSTRAINT repo_customerlist_scenario_id_ed9698c1_fk_repo_scenario_id FOREIGN KEY (scenario_id) REFERENCES public.repo_scenario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_datalog repo_datalog_session_id_7a8d696e_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_datalog
    ADD CONSTRAINT repo_datalog_session_id_7a8d696e_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_datalog repo_datalog_user_id_03f53ea0_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_datalog
    ADD CONSTRAINT repo_datalog_user_id_03f53ea0_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_designteam repo_designteam_organization_id_2ce2d1f4_fk_exper_org; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_designteam
    ADD CONSTRAINT repo_designteam_organization_id_2ce2d1f4_fk_exper_org FOREIGN KEY (organization_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_experorg repo_experorg_organization_id_878492eb_fk_exper_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_experorg
    ADD CONSTRAINT repo_experorg_organization_id_878492eb_fk_exper_organization_id FOREIGN KEY (organization_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_experorg repo_experorg_user_id_3b7e2f80_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_experorg
    ADD CONSTRAINT repo_experorg_user_id_3b7e2f80_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_path repo_path_group_id_4c6d38a9_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_group_id_4c6d38a9_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_path repo_path_plan_id_c1df2ac7_fk_repo_plan_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_plan_id_c1df2ac7_fk_repo_plan_id FOREIGN KEY (plan_id) REFERENCES public.repo_plan(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_path repo_path_session_id_de064431_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_session_id_de064431_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_path repo_path_vehicle_id_4fe4e49b_fk_repo_vehicle_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_vehicle_id_4fe4e49b_fk_repo_vehicle_id FOREIGN KEY (vehicle_id) REFERENCES public.repo_vehicle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_path repo_path_warehouse_id_109b6550_fk_repo_warehouse_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_path
    ADD CONSTRAINT repo_path_warehouse_id_109b6550_fk_repo_warehouse_id FOREIGN KEY (warehouse_id) REFERENCES public.repo_warehouse(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_pathcustomer repo_pathcustomer_customer_id_54cd0293_fk_repo_customer_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_pathcustomer
    ADD CONSTRAINT repo_pathcustomer_customer_id_54cd0293_fk_repo_customer_id FOREIGN KEY (customer_id) REFERENCES public.repo_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_pathcustomer repo_pathcustomer_path_id_b2678cab_fk_repo_path_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_pathcustomer
    ADD CONSTRAINT repo_pathcustomer_path_id_b2678cab_fk_repo_path_id FOREIGN KEY (path_id) REFERENCES public.repo_path(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_plan repo_plan_group_id_e54fe137_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_plan
    ADD CONSTRAINT repo_plan_group_id_e54fe137_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_plan repo_plan_scenario_id_cba976c5_fk_repo_scenario_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_plan
    ADD CONSTRAINT repo_plan_scenario_id_cba976c5_fk_repo_scenario_id FOREIGN KEY (scenario_id) REFERENCES public.repo_scenario(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_plan repo_plan_session_id_a9eb4fda_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_plan
    ADD CONSTRAINT repo_plan_session_id_a9eb4fda_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_profile repo_profile_experiment_id_d7a90e91_fk_exper_experiment_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_experiment_id_d7a90e91_fk_exper_experiment_id FOREIGN KEY (experiment_id) REFERENCES public.exper_experiment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_profile repo_profile_organization_id_514cb12b_fk_exper_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_organization_id_514cb12b_fk_exper_organization_id FOREIGN KEY (organization_id) REFERENCES public.exper_organization(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_profile repo_profile_study_id_2228ba08_fk_exper_study_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_study_id_2228ba08_fk_exper_study_id FOREIGN KEY (study_id) REFERENCES public.exper_study(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_profile repo_profile_team_id_0282cd4d_fk_repo_designteam_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_team_id_0282cd4d_fk_repo_designteam_id FOREIGN KEY (team_id) REFERENCES public.repo_designteam(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_profile repo_profile_user_id_cd227351_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_profile
    ADD CONSTRAINT repo_profile_user_id_cd227351_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_scenario repo_scenario_group_id_25f9c2b8_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenario
    ADD CONSTRAINT repo_scenario_group_id_25f9c2b8_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_scenario repo_scenario_session_id_8a878579_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenario
    ADD CONSTRAINT repo_scenario_session_id_8a878579_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_scenario repo_scenario_warehouse_id_bfa3234e_fk_repo_warehouse_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_scenario
    ADD CONSTRAINT repo_scenario_warehouse_id_bfa3234e_fk_repo_warehouse_id FOREIGN KEY (warehouse_id) REFERENCES public.repo_warehouse(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_vehicle repo_vehicle_group_id_efd51b25_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicle
    ADD CONSTRAINT repo_vehicle_group_id_efd51b25_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_vehicle repo_vehicle_session_id_56e343f8_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_vehicle
    ADD CONSTRAINT repo_vehicle_session_id_56e343f8_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_warehouse repo_warehouse_address_id_a75a4f25_fk_repo_address_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_warehouse
    ADD CONSTRAINT repo_warehouse_address_id_a75a4f25_fk_repo_address_id FOREIGN KEY (address_id) REFERENCES public.repo_address(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_warehouse repo_warehouse_group_id_433c98d8_fk_exper_group_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_warehouse
    ADD CONSTRAINT repo_warehouse_group_id_433c98d8_fk_exper_group_id FOREIGN KEY (group_id) REFERENCES public.exper_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_warehouse repo_warehouse_session_id_f97e0bfc_fk_exper_session_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_warehouse
    ADD CONSTRAINT repo_warehouse_session_id_f97e0bfc_fk_exper_session_id FOREIGN KEY (session_id) REFERENCES public.exper_session(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: repo_waypoint repo_waypoint_customer_id_ab01026c_fk_repo_customer_id; Type: FK CONSTRAINT; Schema: public; Owner: atuser
--

ALTER TABLE ONLY public.repo_waypoint
    ADD CONSTRAINT repo_waypoint_customer_id_ab01026c_fk_repo_customer_id FOREIGN KEY (customer_id) REFERENCES public.repo_customer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

