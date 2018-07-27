import glob
import os
import shutil
import uuid
import zipfile
from cgi import FieldStorage

import geojson
import shapefile
from pyramid.view import view_config

from lokp.config.files import upload_directory_path


class ShapefileProtocol:

    valid_file_types = [
        'application/x-dbf',
        'application/octet-stream',  # Not ideal ...
        'application/x-esri-shape',
        'application/zip',
    ]
    valid_shapes = [shapefile.POLYGON]
    shapefile_required_files = ['.shp', '.dbf', '.shx']

    def __init__(self, request):
        self.request = request
        self.file_fields = []
        self.is_zip_file = False
        self.error = None
        self.geojson = {}
        self.temp_name = str(uuid.uuid4())
        upload_path = upload_directory_path(self.request)
        self.temp_folder = os.path.join(upload_path, f'temp_{self.temp_name}')

    @view_config(route_name='shp_upload', renderer='json')
    def process_uploaded_shapefile(self):
        """
        This function is called as a POST request containing a shapefile
        (actually consisting of several files) or a zip file. The shapefile is
        parsed and if it contains valid geometries, these are returned in
        GeoJSON format.
        :return: dict.
        """
        self.validate_file_types()
        if self.error:
            return self.return_error()

        self.save_files()

        # If uploaded file is a zip file, extract it.
        if len(self.file_fields) == 1 and \
                self.get_file_ending(self.file_fields[0].filename) == '.zip':
            self.extract_zip()

        self.validate_shp_parts()
        if self.error:
            return self.return_error()

        self.read_shapefile()
        if self.error:
            return self.return_error()

        self.remove_temp_dir()

        return self.geojson

    def return_error(self):
        self.request.response.status = 400
        return {'error': self.error}

    def read_shapefile(self):
        """
        Read the shapefile and extract its geometries.
        """
        reader = shapefile.Reader(
            os.path.join(self.temp_folder, self.temp_name))

        if reader.shapeType not in self.valid_shapes:
            self.error = 'Invalid geometry.'
            return

        geometries = []
        for shape in reader.shapes():
            geom = shape.__geo_interface__
            geometries.append(geojson.GeoJSON(geom))

        if len(geometries) != 1:
            # If there are multiple features, create a single MultiPolygon out
            # of them.
            coordinates = [geom['coordinates'] for geom in geometries]
            geometries = [geojson.MultiPolygon(tuple(coordinates))]

        self.geojson = geojson.dumps(geometries[0])

    def extract_zip(self):
        # zip_file = ''
        # target_dir = ''
        # with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        #     zip_ref.extractall(target_dir)
        self.error = 'TODO ...'
        return

    def validate_shp_parts(self):
        """
        Check that all files of a valid shapefile are available.
        """
        file_endings = [
            self.get_file_ending(filename) for filename in glob.glob(
                os.path.join(self.temp_folder, '*'))]

        missing_parts = set(self.shapefile_required_files) - set(file_endings)
        if missing_parts:
            self.error = 'Missing required parts of shapefile: %s' % ', '.join(
                missing_parts)
            return

    def save_files(self):
        """
        Save uploaded files to a temporary location.
        """
        # Create temporary upload directory
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        # Save all files
        for field in self.file_fields:
            input_file = field.file

            # Prepare file name
            file_ending = self.get_file_ending(field.filename)
            file_path = os.path.join(
                self.temp_folder, f'{self.temp_name}{file_ending}')

            # Create a temporary file to prevent incomplete files from being
            # used.
            temp_file_path = f'{file_path}~'
            input_file.seek(0)
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)

            # Rename the temporary file
            os.rename(temp_file_path, file_path)

    def validate_file_types(self):
        """
        Check that only valid file types are being sent.
        """
        file_fields = []
        for data in self.request.POST.items():
            field = data[1]
            if not isinstance(field, FieldStorage):
                continue
            file_fields.append(field)

        invalid_file_types = set(
            [f.type for f in file_fields]) - set(self.valid_file_types)
        if invalid_file_types:
            self.error = 'Invalid file types: %s' % ', '.join(
                invalid_file_types)
            return

        self.file_fields = file_fields

    def remove_temp_dir(self):
        pass

    @staticmethod
    def get_file_ending(filename) -> str:
        """Return the ending (e.g. ".shp") of a filename."""
        return os.path.splitext(filename)[1]
