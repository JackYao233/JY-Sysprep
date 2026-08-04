import os
import shutil


def clean_temp():

    paths = [

        r"C:\Windows\Temp",

        os.environ.get(
            "TEMP"
        )

    ]


    for path in paths:

        if not path:
            continue


        if os.path.exists(path):

            try:

                for item in os.listdir(path):

                    item_path = os.path.join(
                        path,
                        item
                    )

                    try:

                        if os.path.isfile(item_path):

                            os.remove(item_path)


                        elif os.path.isdir(item_path):

                            shutil.rmtree(
                                item_path,
                                ignore_errors=True
                            )

                    except:

                        pass


            except:

                pass


    return True