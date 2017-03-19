import shelve

DB_FILE_NAME = 'mydb'


class DBHelper(object):
    def __init__(self, db_file_name="mydb"):
        self.db = shelve.open(db_file_name, writeback=True)
        self.last_processed_id = 'last_processed_id'
        self.min_lat_lon = 'min_lat_lon'
        self.max_lat_lon = 'max_lat_lon'

    def update_min_max_coordinate(self, min_lat_lon, max_lat_lon):
        """
        :param min_lat_lon: (min lat, min lon)
        :type min_lat_lon: tuple
        :param max_lat_lon: (max lat, max lon)
        :type max_lat_lon: tuple
        :return: None
        :rtype: None
        """
        self.db[self.min_lat_lon] = min_lat_lon
        self.db[self.max_lat_lon] = max_lat_lon
        self.save()

    def get_min_lat_lon(self):
        if self.min_lat_lon not in self.db:
            return None, None
        return self.db[self.self.min_lat_lon]

    def get_max_lat_lon(self):
        if self.max_lat_lon not in self.db:
            return None, None
        return self.db[self.self.max_lat_lon]

    def save(self):
        self.db.sync()

    def get_last_processed_row_id(self):
        if self.last_processed_id not in self.db:
            return -1
        return self.db[self.last_processed_id]

    def update_last_processed_row_id(self, row_id):
        self.db[self.last_processed_id] = row_id
        self.db.sync()


def from_csv_to_js(csv_file_path, js_file_path):
    with open(csv_file_path) as fr:
        header = None
        with open(js_file_path, "w") as fw:
            print("var data = [ ", file=fw)
            for line in fr:
                if header is None:
                    header = line
                    continue
                print("[{}]".format(line.strip()), file=fw, end=",")
            print("]", file=fw)
            fw.close()
        fr.close()
