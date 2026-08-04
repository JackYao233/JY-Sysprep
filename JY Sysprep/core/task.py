from abc import ABC, abstractmethod



class Task(ABC):


    name="Unknown"



    @abstractmethod
    def execute(self, context):

        pass



    def rollback(self):

        pass