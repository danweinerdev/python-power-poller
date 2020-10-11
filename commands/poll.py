from monitor.lib import ConversionFailure, Metric, Result
from tplink.discover import LoadDevice
from tplink.utils import IsValidIPv4


def ProcessDevice(pipeline, name, config, logger=None):
    address = config['address']
    if not IsValidIPv4(address):
        if logger:
            logger.error('Invalid device configuration: {}', name)
        return False

    device = LoadDevice(address)
    if not device.HasEmeter():
        if logger:
            logger.warning("Device '{}' does not support electronic metering",
                device.GetAlias())
        return False

    emeter = device.GetEmeter()
    result = emeter.GetRealtime(cache=False)
    if 'err_code' not in result or result['err_code'] != 0:
        if logger:
            logger.error("Failed to load device '{}' emeter data",
                device.GetAlias())
        return False

    for key, value in result.items():
        if key not in config['fields']:
            continue
        try:
            pipeline(Metric(name, key, value))
        except ConversionFailure:
            if logger:
                logger.error("Failed to convert value '{}' for metric '{}'"
                    .format(value.strip(), key))

    return True


def Poll(config, logger, pipeline):
    success = True
    for device, cfg in config.items():
        if ProcessDevice(pipeline, device, cfg, logger=logger):
            success = False
    return Result.CANCEL if success else Result.FAILURE
