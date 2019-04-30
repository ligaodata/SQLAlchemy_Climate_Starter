
# Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

# import Flask
from flask import Flask, jsonify

# Create a engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
#Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# Create an app, being sure to pass __name__

app= Flask(__name__)

# Homepage and list all routes that are available
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available API Routes Endpoints:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/precipitation")
def precipitation():
#Return a JSON list of precipitation data 
    prcp = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()
    
    
    prcp_dict={} 
    for i in range(len(prcp)):
        prcp_dict[prcp[i][0]]= prcp[i][1] 

    return jsonify(prcp_dict)

@app.route("/api/stations")
# Return a JSON list of stations from the dataset.
def stations():
    station_list = session.query(Measurement.station).all()
    station_list = list(set(station_list))
    station_list = list(np.ravel(station_list))
    return jsonify(station_list)

@app.route("/api/temperature")
def temperature():
    """
    We have known that The latest date in the dateset is 2017-08-23
    The date 1 year ago from the last date is 2016-08-23.
    """
    date_tem_list= session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date>="2016-08-23").order_by(Measurement.date).all()
    date_tem_dic={}
    for i in range(len(date_tem_list)):
        date_tem_dic[date_tem_list[i][0]]= date_tem_list[i][1]
    
    return  jsonify(date_tem_dic)
    
@app.route("/api/v1.0/<start>")
#Return a JSON list of the min, avg, and max tobs data for all dates no earlier than the start date
def date_start(start):
    """
        Args: 
        start(string): a date string in the format '%y-%m-%d'
    """
    tem_start_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    tem_start_dic = {"TMIN": tem_start_list[0][0],"TAVG": tem_start_list[0][1],"TMAX": tem_start_list[0][2]} 
    return jsonify(tem_start_dic)


@app.route("/api/v1.0/<start>/<end>")
def date_start_end(start, end):
    """
    Args: 
        start(string): a date string in the format '%y-%m-%d'
        end(string): a date string in the format '%y-%m-%d'
    """
    # Check if end date is later than start date
    if start >= end:  
        return f' Please double-check your query input!'
        
    else:
        tem_start_end_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

        tem_start_end_dic = {"TMIN": tem_start_end_list[0][0],"TAVG": tem_start_end_list[0][1],\
            "TMAX": tem_start_end_list[0][2]} 
        return jsonify(tem_start_end_dic)


if __name__ == "__main__":
    app.run(debug=True) 