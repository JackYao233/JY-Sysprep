from abc import ABC, abstractmethod



class SysprepAdapter(ABC):


    """
    JY Sysprep 系统封装适配器基类

    所有Windows版本必须继承此类
    """



    name = "Unknown"


    version = "Unknown"



    def __init__(self, context):

        self.context = context



    @abstractmethod
    def check_support(self):

        """
        检查当前系统是否支持该封装模块
        """

        pass



    @abstractmethod
    def prepare(self):

        """
        封装前准备
        """

        pass



    @abstractmethod
    def generate_unattend(self):

        """
        生成无人值守文件
        """

        pass



    @abstractmethod
    def cleanup(self):

        """
        封装前清理
        """

        pass