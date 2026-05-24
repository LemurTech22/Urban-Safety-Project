import pandera.pandas as pa
from pandera import Column, Check

schema = pa.DataFrameSchema(
    columns = {
        "crash_date_time":  Column(str, nullable=False),
        "acrs_report_type": Column(str, nullable=False,
                                   checks=Check.isin([
                                       "Property Damage Crash",
                                       "Injury Crash",
                                       "Fatal Crash"
                                   ])),
        "collision_type":    Column(str, nullable=False),
        "route_type":        Column(str, nullable=False),
        "road_name":         Column(str, nullable=False),
        "cross_street_name": Column(str, nullable=True),
        "latitude":          Column(str, nullable=False,
                                checks=Check(
                                    lambda s: s.astype(float).between(-90, 90).all(),
                                    error="latitude out of range"
                                )),
        "longitude":         Column(str, nullable=False,
                                checks=Check(
                                    lambda s: s.astype(float).between(-180, 180).all(),
                                    error="longitude out of range"
                                )),
        
        "weather":              Column(str, nullable=False),
        "surface_condition":    Column(str, nullable=False),
        "light":                Column(str, nullable=False),
        "traffic_control":      Column(str, nullable=False),

        "driver_substance_abuse":   Column(str, nullable=False),
        "driver_at_fault":          Column(str, nullable=False,
                                        checks=Check.isin(["Yes", "No", "Unknown"])),
        "injury_severity":          Column(str, nullable=False),
        "circumstance":             Column(str, nullable=True),
        "driver_distracted_by":     Column(str, nullable=False),
        "drivers_license_state":    Column(str, nullable=True),

        "vehicle_damage_extent":        Column(str, nullable=False),
        "vehicle_first_impact_location":Column(str, nullable=False),
        "vehicle_body_type":            Column(str, nullable=False),
        "vehicle_movement":             Column(str, nullable=True),
        "vehicle_going_dir":            Column(str, nullable=True),
        "speed_limit":                  Column(str, nullable=False,
                                            checks=Check(
                                                lambda s: s.astype(int).between(0, 100).all(),
                                                error="speed_limit out of range"
                                            )),
        "driverless_vehicle":           Column(str, nullable=False,
                                            checks=Check.isin(["Yes", "No"])),
        "parked_vehicle":               Column(str, nullable=False,
                                            checks=Check.isin(["Yes", "No"])),
        "vehicle_year":                 Column(str, nullable=False),
        "vehicle_make":                 Column(str, nullable=True),
        "vehicle_model":                Column(str, nullable=True),

    },
    checks=[
        Check(lambda df: len(df) > 100, error="Row count too low")
    ]
)
