-- Table: public.category

-- DROP TABLE public.category;

CREATE TABLE public.category
(
    category_id bigint NOT NULL,
    category_shortname character varying COLLATE pg_catalog."default",
    category_name character varying COLLATE pg_catalog."default",
    CONSTRAINT category_pkey PRIMARY KEY (category_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.category
    OWNER to dsci6007;
COMMENT ON TABLE public.category
    IS 'This will store the category information of each meeting.';

-- Table: public.meeting

-- DROP TABLE public.meeting;

CREATE TABLE public.meeting
(
    meeting_id bigint NOT NULL,
    category_id bigint,
    city character varying COLLATE pg_catalog."default",
    longitude bigint,
    latitude bigint,
    members integer,
    url character varying COLLATE pg_catalog."default",
    name character varying COLLATE pg_catalog."default",
    description text COLLATE pg_catalog."default",
    member_id bigint,
    CONSTRAINT meeting_pkey PRIMARY KEY (meeting_id),
    CONSTRAINT category_fk FOREIGN KEY (category_id)
        REFERENCES public.category (category_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT member_fk FOREIGN KEY (member_id)
        REFERENCES public.member (member_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.meeting
    OWNER to dsci6007;
COMMENT ON TABLE public.meeting
    IS 'To store MeetUp meeting information.';

-- Table: public.meeting_topic

-- DROP TABLE public.meeting_topic;

CREATE TABLE public.meeting_topic
(
    meeting_id bigint NOT NULL,
    topic_id bigint NOT NULL,
    CONSTRAINT meeting_topics_pkey PRIMARY KEY (meeting_id, topic_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.meeting_topic
    OWNER to dsci6007;
COMMENT ON TABLE public.meeting_topic
    IS 'Join table to lookup topics per meeting.';

-- Table: public.member

-- DROP TABLE public.member;

CREATE TABLE public.member
(
    member_id bigint NOT NULL,
    member_name character varying COLLATE pg_catalog."default",
    CONSTRAINT member_pkey PRIMARY KEY (member_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.member
    OWNER to dsci6007;
COMMENT ON TABLE public.member
    IS 'This is to store the MeetUp member that creates/organizes a meeting.';

-- Table: public.topic

-- DROP TABLE public.topic;

CREATE TABLE public.topic
(
    topic_id bigint NOT NULL,
    topic_name character varying COLLATE pg_catalog."default",
    topic_urlkey character varying COLLATE pg_catalog."default",
    CONSTRAINT topic_pkey PRIMARY KEY (topic_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.topic
    OWNER to dsci6007;
COMMENT ON TABLE public.topic
    IS 'This will store all topics for a given meeting.';

-- Table: public.spatial_ref_sys

-- DROP TABLE public.spatial_ref_sys;

CREATE TABLE public.spatial_ref_sys
(
    srid integer NOT NULL,
    auth_name character varying(256) COLLATE pg_catalog."default",
    auth_srid integer,
    srtext character varying(2048) COLLATE pg_catalog."default",
    proj4text character varying(2048) COLLATE pg_catalog."default",
    CONSTRAINT spatial_ref_sys_pkey PRIMARY KEY (srid),
    CONSTRAINT spatial_ref_sys_srid_check CHECK (srid > 0 AND srid <= 998999)
)
WITH (
    OIDS = FALSE
)


TABLESPACE pg_default;

ALTER TABLE public.spatial_ref_sys
    OWNER to rdsadmin;

GRANT ALL ON TABLE public.spatial_ref_sys TO rdsadmin;

GRANT SELECT ON TABLE public.spatial_ref_sys TO PUBLIC;