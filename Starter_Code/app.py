# Import the dependencies.
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement=Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB

#done in each route

#################################################
# Flask Setup
#################################################
app=Flask(__name__)




#################################################
# Flask Routes
#################################################

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation(): 
    session=Session(bind=engine)
    one_yr_ago_date= dt.date(2017,8,23) - relativedelta(years=+1)
    
    date_prcp= session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>= one_yr_ago_date).all()
    results={}
    
    for date, prcp in date_prcp:
        results[date]=prcp
    session.close()
    
    return jsonify(results)
    
#Return a JSON list of stations from the dataset.   
@app.route('/api/v1.0/station')
def station(): 
    
    session=Session(bind=engine)

    stations= session.query(Station.station).all()
    stations_list=list(np.ravel(stations))
    session.close()
    
    return jsonify(stations_list)
    
    
#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session=Session(bind=engine)
    
    most_recent_date= session.query(Measurement.date).order_by(Measurement.date.desc()).\
    filter(Measurement.station =='USC00519281').first()

    one_yr_ago_date= dt.date(2017,8,18) - relativedelta(years=+1)

    temp_data= session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.date >= one_yr_ago_date).all()
    
    results={}
    for tobs, date in temp_data:
        results[tobs]=date
        
    session.close()
    
    return jsonify(results)

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def start_end(start=None,end=None):
    session=Session(bind=engine)
    #if no end date is put into the URL, follow this path
    if not end:
        temp_data=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=dt.date(2017,8,18)).all()
        
        temps=list(np.ravel(temp_data))
        session.close()
        return jsonify(temps)
    #if both start and end date are put into URL, follow this path
    temp_data=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date>=start).\
        filter(Measurement.date<=end).all()
    
    temps=list(np.ravel(temp_data))
    session.close()
    return jsonify(temps)


if __name__ == "__main__" :
    app.run(debug=True)