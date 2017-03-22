-- Table: public.al_overview

-- DROP TABLE public.al_overview;

CREATE TABLE public.al_overview
(
    al_account_id bigint NOT NULL,
    account_name text COLLATE pg_catalog."default" NOT NULL,
    tm_appliance_count bigint,
    tm_policies_count bigint,
    tm_protected_hosts_count bigint,
    tm_hosts_count bigint,
    insert_ts timestamp with time zone NOT NULL DEFAULT now()
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.al_overview
    OWNER to dbadmin;

GRANT ALL ON TABLE public.al_overview TO dbadmin;

GRANT SELECT ON TABLE public.al_overview TO php_readonly;

COMMENT ON TABLE public.al_overview
    IS 'Summary Metrics from Alert Logic';

