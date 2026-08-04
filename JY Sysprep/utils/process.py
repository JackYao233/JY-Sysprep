class Context:

    def __init__(self):

        # Windows版本
        self.os_version = None

        # Build号
        self.build = None

        # CPU架构
        self.arch = None

        # 是否管理员
        self.is_admin = False


    def show(self):

        print("====== System Context ======")

        print(
            "Windows:",
            self.os_version
        )

        print(
            "Build:",
            self.build
        )

        print(
            "Architecture:",
            self.arch
        )

        print(
            "Administrator:",
            self.is_admin
        )