#!/bin/sh

cp actionlog_base.py ../core/actionlog.py
python auto_make_actionlog.py >> ../core/actionlog.py

cp derivedlog_base.py ../core/derivedlog.py
python auto_make_derivedlog.py >> ../core/derivedlog.py

cp types_base.py ../core/types.py
python auto_make_types.py >> ../core/types.py
