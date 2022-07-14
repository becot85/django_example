# Import necessary packages
from django.db import models


# FileDescription class
# =====================
class FileDescription(models.Model):

    '''

    General description of a file entry found within the input csv file,
    including FileName, FilePath, and Size, and derived FileExtension and
    UniformSize.

    '''

    # Declare variables describing one entry of the original csv file
    file_name = models.CharField(max_length=50)
    file_path = models.CharField(max_length=100)
    size = models.CharField(max_length=10)

    # Declare variables derived from the original variables
    file_extension = models.CharField(max_length=10)
    uniform_size = models.FloatField()


    # String operator
    # ===============
    def __str__(self):
        return self.file_name + " ---- " + self.file_path + " ---- " + self.size


