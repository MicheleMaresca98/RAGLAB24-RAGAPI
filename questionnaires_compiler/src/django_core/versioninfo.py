class VersionInfo:
    PRODUCT: str = "questionnaires_compiler"
    VERSION: str = "1.0.0"
    COMPANY: str = "RagLabTeam2"
    COPYRIGHT: str = ""
    TRADEMARKS: str = ""
    DESCRIPTION: str = ""
    COMMENTS: str = ""
    VATNUMBER: str = ""
    FISCAL_CODE: str = ""

    @staticmethod
    def version():
        return VersionInfo.VERSION


VERSION = VersionInfo.version()
