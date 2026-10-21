class OSProfile:


    def __init__(self):

        # 基础信息

        self.family = None

        self.product_name = None

        self.edition = None

        self.build = None

        self.display_version = None


        # NT版本

        self.nt_version = None


        # 系统类型

        self.is_server = False

        self.installation_type = None


        # 硬件

        self.architecture = None


        # 权限

        self.is_admin = False


        # Sysprep

        self.sysprep_path = None



    def show(self):

        print("==============================")

        print(
            "系统:",
            self.family
        )

        print(
            "产品:",
            self.product_name
        )

        print(
            "版本:",
            self.display_version
        )

        print(
            "Build:",
            self.build
        )

        print(
            "Edition:",
            self.edition
        )

        print(
            "NT:",
            self.nt_version
        )

        print(
            "Server:",
            self.is_server
        )

        print(
            "架构:",
            self.architecture
        )

        print("==============================")