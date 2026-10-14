from sysprep.configured_adapter import ConfiguredWindowsAdapter


SUPPORTED_FAMILIES = {
    "Windows Vista",
    "Windows 7",
    "Windows 8",
    "Windows 8.1",
    "Windows 10",
    "Windows 11",
    "Windows Server 2008",
    "Windows Server 2008 R2",
    "Windows Server 2012",
    "Windows Server 2012 R2",
    "Windows Server 2016",
    "Windows Server 2019",
    "Windows Server 2022",
    "Windows Server 2025",
}


class AdapterFactory:
    @staticmethod
    def create(context):
        if context.family in SUPPORTED_FAMILIES:
            return ConfiguredWindowsAdapter(context, context.family)
        return None
