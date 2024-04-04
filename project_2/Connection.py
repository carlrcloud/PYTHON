connection = Connection(
    server,
    user=user_info,
    password=pwd
)

if not connection.bind():
    logger.info("unable to bind the AD server")
    raise Exception("failed to connect to active directory")
logger.info("successfully connected to active directory")