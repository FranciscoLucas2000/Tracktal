from prefect import flow, get_run_logger


@flow(name="smoke-test")
def smoke_test():
    logger = get_run_logger()
    logger.info("Prefect on Railway: OK")
    return "ok"
