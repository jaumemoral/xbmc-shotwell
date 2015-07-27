'''
Shotwell BD Access
'''

import os
import sqlite3
import datetime


class Shotwell:

    def __init__(self, settings):
        path_db = self.resolve_path_db(settings)
        path_thumbs = self.resolve_path_thumbs(settings)
        self.thumbs128 = '%s/thumbs128' % (path_thumbs)
        self.thumbs360 = '%s/thumbs360' % (path_thumbs)
        self.conn = sqlite3.connect(path_db)
        self.conn.isolation_level = None

    def resolve_path_db(self, settings):
        path_db = settings.getSetting("path_db")
        if os.path.isfile(path_db):
            return path_db
        path_db = settings.getSetting("path_db2")
        if os.path.isfile(path_db):
            return path_db
        path_db = os.path.expanduser("~/.local/share/shotwell/data/photo.db")
        if os.path.isfile(path_db):
            return path_db
        path_db = os.path.expanduser("~/.shotwell/data/photo.db")
        if os.path.isfile(path_db):
            return path_db
        return ""

    def resolve_path_thumbs(self, settings):
        thumbs = settings.getSetting("path_thumbs")
        if os.path.isdir(thumbs):
            return thumbs
        thumbs = settings.getSetting("path_thumbs2")
        if os.path.isdir(thumbs):
            return thumbs
        thumbs = os.path.expanduser("~/.cache/shotwell/thumbs")
        if os.path.isdir(thumbs):
            return thumbs
        thumbs = os.path.expanduser("~/.shotwell/thumbs")
        if os.path.isdir(thumbs):
            return thumbs
        return ""

    def picture_list(self, condition="1=1", order="exposure_time", flagged=False):
        select = 'select id, filename from phototable'
        if flagged:
            condition += " and flags=16"

        sql = ' '.join([select, 'where', condition, 'order by', order])

        cursor = self.conn.cursor()
        rows = cursor.execute(sql)

        l = list(
            {'id': row[0],
            'name': os.path.basename(row[1]),
            'filename': row[1],
            'icon': '%s/thumb%016x.jpg' % (self.thumbs128, row[0]),
            'thumbnail': '%s/thumb%016x.jpg' % (self.thumbs360, row[0])}
            for row in rows)

        cursor.close()
        return l

    def picture_list_flagged(self):
        return self.picture_list(flagged=True)

    def picture_list_event(self, event_id, flagged):
        return self.picture_list(condition="event_id=%s" % (event_id), flagged=flagged)

    def picture_list_last(self, flagged):
        return self.picture_list(condition="import_id = (select max(import_id) from phototable)", flagged=flagged)

    def picture_list_tag(self, tag_id, flagged):
        # get a comma separated thumbnail list from a database field
        cursor = self.conn.cursor()
        cursor.execute(
            'select photo_id_list from tagtable where id=%i' % (tag_id))
        row = cursor.fetchone()
        cursor.close()
        thumbs = row[0].split(",")
        thumbs.pop()
        # and transform to a decimal number list after converting it from
        # hexadecimal
        l = list(str(int(f[6:], 16)) for f in thumbs)
        return self.picture_list(condition='id in (%s)' % (','.join(l)), flagged=flagged)

    def event_list(self):
        cursor = self.conn.cursor()
        rows = cursor.execute('''
            select e.id, name, min(p.exposure_time) as start,max(p.exposure_time) as end, primary_source_id
            from eventtable e,phototable p where event_id=e.id
            group by event_id order by 3 desc
        ''')
        l = []
        for row in rows:
            l.append({
                'id': row[0],
                'name': row[1],
                'start': datetime.datetime.fromtimestamp(row[2]),
                'end': datetime.datetime.fromtimestamp(row[3]),
                'icon': '%s/%s.jpg' % (self.thumbs128, row[4]),
                'thumbnail': '%s/%s.jpg' % (self.thumbs360, row[4])
            })
        return l

    def tag_list(self):
        cursor = self.conn.cursor()
        rows = cursor.execute('select id, name from tagtable')
        l = []
        for row in rows:
            l.append({
                'id': row[0],
                'name': row[1]
            })
        return l
