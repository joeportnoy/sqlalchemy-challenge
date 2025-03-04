# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, jsonify, render_template

import datetime as dt
import pandas as pd


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return(
        f"Available Routes:<br />"
        f"/api/v1.0/precipitation<br />"
        f"/api/v1.0/stations<br />"
        f"/api/v1.0/tobs<br />"
        f"/api/v1.0/<start><br />"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores (columns = date and prcp)
    sel = [Measurement.date, Measurement.prcp]
    year_preciptation = session.query(*sel).\
        filter(Measurement.date >= last_year).all()
    
    session.close()

    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    precipitation_df = pd.DataFrame(year_preciptation, columns=['date', 'precipitation'])

    # Sort the dataframe by date
    precipitation_df = precipitation_df.sort_values(by='date') 

    precipitation_dict = precipitation_df.set_index('date')['precipitation'].to_dict()

    #JSONify
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Query station names
    station_names = session.query(Station.name).all()

    session.close()

    #Gather station names into a list
    all_station_names = list(np.ravel(station_names))

    #JSONify
    return jsonify(all_station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    sel = [Measurement.date, Measurement.tobs]
    year_temp_data_USC00519281 = session.query(*sel).\
            filter(Measurement.date >= last_year,
            Measurement.station == 'USC00519281').all()
    
    session.close()

    #Create a DataFrame to save the data before plotting
    USC00519281_temp_df = pd.DataFrame(year_temp_data_USC00519281, columns=['date', 'temp'])

    temp_list = USC00519281_temp_df.to_dict(orient='records')

    #JSONify
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def date_start(start):

    session = Session(engine)

    #Calculate lowest, highest, and average temperatures
    station_data_temps = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    session.close()

    if station_data_temps[0][0] is None:
        return jsonify({"ERROR": "No data found for the specified start date."}), 404

    temp_stats = {
        "Lowest Temperature": station_data_temps[0][0],
        "Highest Temperature": station_data_temps[0][1],
        "Average Temperature": station_data_temps[0][2]
    }

    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    
    session = Session(engine)

    #Calculate lowest, highest, and average temperatures
    station_data_temps = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    if station_data_temps[0][0] is None:
        return jsonify({"ERROR": "No data found for the specified date range."}), 404

    temp_stats = {
        "Lowest Temperature": station_data_temps[0][0],
        "Highest Temperature": station_data_temps[0][1],
        "Average Temperature": station_data_temps[0][2]
    }

    return jsonify(temp_stats)


if __name__ == '__main__':
    app.run(debug=True)
