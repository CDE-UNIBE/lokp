import glob
import os
import shutil
import uuid
import zipfile
from cgi import FieldStorage

import geojson
import geopandas
from fiona.errors import FionaValueError
from pyramid.view import view_config

from lokp.config.files import upload_directory_path


class ShapefileProtocol:

    valid_file_types = [
        'application/x-dbf',
        'application/octet-stream',  # Not ideal ...
        'application/x-esri-shape',
        'application/zip',
    ]
    valid_shapes = ['Polygon']
    shapefile_required_files = ['.shp', '.dbf', '.shx']
    default_crs = 'epsg:4326'

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
        """
        An error occured. Return with appropriate status code and error message.
        """
        self.remove_temp_dir()
        self.request.response.status = 400
        return {'error': self.error}

    def read_shapefile(self):
        """
        Read the shapefile and extract its geometries.
        """
        # When extracting zip files, we need to find out the name of the
        # shapefile
        shapefile_path = self.find_shp_in_directory(self.temp_folder)

        try:
            geom_data_frame = geopandas.read_file(shapefile_path)
        except FionaValueError:
            self.error = 'Invalid file.'
            return

        # If the data is not in the default CRS, reproject it.
        if geom_data_frame.crs.get('init') != self.default_crs:
            geom_data_frame = geom_data_frame.to_crs({'init': self.default_crs})

        # Check geometry types.
        for index, row in geom_data_frame.iterrows():
            if row.geometry.geom_type not in self.valid_shapes:
                self.error = 'Invalid geometry.'
                return

        # The server must return only the geometry part(s) of the features, not
        # the entire geojson.
        geom_json = geojson.loads(geom_data_frame.to_json())
        geometries = [f['geometry'] for f in geom_json['features']]

        if len(geometries) != 1:
            # If there are multiple features, create a single MultiPolygon out
            # of them.
            coordinates = [geom['coordinates'] for geom in geometries]
            geometries = [geojson.MultiPolygon(tuple(coordinates))]

        self.geojson = geojson.dumps(geometries[0])

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

    def extract_zip(self):
        """
        Extract an uploaded zipfile to the temporary location.
        """
        file_ending = self.get_file_ending(self.file_fields[0].filename)
        file_path = os.path.join(
            self.temp_folder, f'{self.temp_name}{file_ending}')

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_folder)

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
        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder)

    @staticmethod
    def get_file_ending(filename) -> str:
        """Return the ending (e.g. ".shp") of a filename."""
        return os.path.splitext(filename)[1]

    @staticmethod
    def find_shp_in_directory(dir_path: str) -> str:
        """
        Return the path of the shapefile (*.shp) in a directory.
        ATTENTION: This returns only the first occurrence found!
        """
        shapefiles = glob.glob(os.path.join(dir_path, '*.shp'))
        if len(shapefiles) > 0:
            return shapefiles[0]
