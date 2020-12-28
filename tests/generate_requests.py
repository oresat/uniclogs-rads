import sys; sys.path.insert(0, '../src/rads/database')
import random
import string
from datetime import datetime, timedelta
import pass_calculator.calculator as pc
from rads.database.models import Request, Pass, Session
import pytest

tle = [
    "1 25544U 98067A   20185.75040611  .00000600  00000-0  18779-4 0  9992",
    "2 25544  51.6453 266.4797 0002530 107.7809  36.4383 15.49478723234588"
    ]

# oregon as a box
MinLongitude = -116.926326
MaxLatitude = 46.211947
MaxLongitude = -124.001521
MinLatitude = 41.990853


days_in_past = 2
start = datetime.utcnow()
start = start - timedelta(days=days_in_past)
start = start


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@pytest.mark.skip(reason='Turn DB tests into magic mock')
def test_generated_passes(num: int):
    generated_passes = []

    for i in range(num):
        days = random.randrange(days_in_past+7)
        start_day = start + timedelta(days=days)
        start_day = start_day
        end_day = start_day + timedelta(days=1)
        end_day = end_day

        latitude = round(random.uniform(MinLatitude, MaxLatitude), 6)
        longitude = round(random.uniform(MinLongitude, MaxLongitude), 6)
        elevation_m = round(random.uniform(0.0, 2000.0), 2)

        # call pass calculator
        orbital_passes = pc.get_all_passes(
                tle=tle,
                lat_deg=latitude,
                long_deg=longitude,
                start_datetime_utc=start_day,
                end_datetime_utc=end_day,
                elev_m=elevation_m
                )

        index = random.randrange(len(orbital_passes))
        generated_passes.append(orbital_passes[index])

    return generated_passes


@pytest.mark.skip(reason='Turn DB tests into magic mock')
def test_insert_into_db(generated_passes, random_status=False):
    session = Session()
    ret = []

    for p in generated_passes:

        # look for pass in db
        result = session.query(Pass)\
            .filter(Pass.start_time == p.aos_utc,
                    Pass.latitude == p.gs_latitude_deg,
                    Pass.longitude == p.gs_longitude_deg)\
            .first()

        if result is None:
            # pass not in db, add it
            new_pass = Pass(
                latitude=p.gs_latitude_deg,
                longitude=p.gs_longitude_deg,
                elevation=p.gs_elevation_m,
                start_time=p.aos_utc,
                end_time=p.los_utc
                )

            session.add(new_pass)
            session.flush()

            pass_uid = new_pass.uid
        else:
            # pass already in db
            pass_uid = result.uid

        # random statuses
        if random_status is True:
            approved_status = random.choice([True, False, None])
            sent_status = random.choice([True, False])
        else:
            approved_status = None
            sent_status = False

        # make a random created_dt
        days = random.randrange(14)
        hours = random.randrange(24)
        mins = random.randrange(60)
        secs = random.randrange(60)
        created_dt = start - timedelta(days=days, hours=hours, minutes=mins, seconds=secs)
        created_dt = created_dt

        new_request = Request(
            user_token=randomword(10),
            is_approved=approved_status,
            is_sent=sent_status,
            pass_uid=pass_uid,
            observation_type=random.choice(["cfc", "oresat live", "uniclogs"]),
            created_date=created_dt
            )

        session.add(new_request)
        session.flush()

        ret.append(new_request.uid)

    session.commit()
    session.close()

    return ret


@pytest.mark.skip(reason='Turn DB tests into magic mock')
def test_clear_db():
    session = Session()

    result = session.query(Request).all()

    for r in result:
        session.delete(r)

    result = session.query(Pass).all()

    for r in result:
        session.delete(r)

    session.commit()
    session.close()


# if __name__ == '__main__':
#     num = 100
#     random_status = False
#
#     opts, argv = getopt.getopt(sys.argv[1:], "hcrn:")
#     for o, a in opts:
#         if o == '-h':
#             print("""
#             Flags
#             -h   : help message
#             -r   : randomize is_approved and is_sent statuses
#             -n x : generate x passes where x > 0 and x < 10000
#             -c   : clean db
#             None : gererate 100 non randomize requests
#             """)
#             exit(0)
#         elif o == '-c':
#             clear_db()
#             exit(0)
#         elif o == '-r':
#             random_status = True
#         elif o == '-n':
#             v = int(a)
#             if v < 0 or v >= 10000:
#                 print("Can't be negative or greater than 10000")
#                 exit(0)
#             num = v
#         else:
#             print("Unkown flag, run with -h for help message")
#             exit(1)
#
#     pass_list = generated_passes(num)
#     req = insert_into_db(pass_list, random_status)
