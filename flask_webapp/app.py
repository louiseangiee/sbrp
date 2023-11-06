from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from db_config import db
from decouple import config
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy
from db_config.models import *
# from db_config.models import Role_Listing, Application, Country, Department, Skill, Staff, Access_Control, Role, Role_Skill, Staff_Skill
from sqlalchemy import text, asc, desc
from sqlalchemy import and_, or_
import json
import requests
from authorisation import login_required
import traceback

# from fuzzywuzzy import fuzz

def create_app(test_config=None):
    # Create the Flask application
    app = Flask(__name__)

    # Configure the application
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = config("SECRET_KEY")

    if test_config is not None:
        # Load the test config if passed in
        app.config.update(test_config)
    else:
        # Otherwise, load the config from the environment variable
        app.config["SQLALCHEMY_DATABASE_URI"] = config("DATABASE_URL")

    # Initialize plugins
    db.init_app(app)
    
    # Additional setup, such as registering blueprints, can go here

    return app

app = create_app()


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/pagination_counter")
def pagination_counter():
    listings_json = get_all_open_role_listings(False)
    listings_dict = json.loads(listings_json.data)
    listings = listings_dict["data"]
    num_results = len(listings)
    print(num_results)
    pages_required = 1
    if num_results == 0:
        pass
    else:
        pages_required = (num_results + 3 - 1) // 3
    return str(pages_required)


@app.route("/calculate_pages_required")
def calculate_num_listings(search):
    from db_config.models import Role_Listing
    if search == None:
        current_time = datetime.now()
        role_listings = (
            Role_Listing.query.filter(
                and_(
                    Role_Listing.date_open <= current_time,
                    Role_Listing.date_close >= current_time,
                    Role_Listing.num_opening > 0,
                    Role_Listing.date_close >= current_time,
                )
            )
            .order_by(desc(Role_Listing.date_open))
            .all()
        )
        print(role_listings)
        num_role_listings = len(role_listings)
        print(f"Number of role listings: {num_role_listings}")

        listings_per_page = 5

        pages_required = (
            num_role_listings + listings_per_page - 1
        ) // listings_per_page
        print(
            f"Number of pages required ({listings_per_page} listings per page): {pages_required}"
        )
        result = {
            "pages_required": pages_required,
            "num_role_listings": num_role_listings,
        }
        return result
    else:
        if search:

            role_name = search["role_search"]
            recency = search["recency"]
            country = search["country"]
            department = search["department"]
            required_skills = search["required_skills"]
            print(department)
            print(required_skills)
            print("test here")

            current_time = datetime.now()
            base_query = Role_Listing.query.filter(
                and_(
                    Role_Listing.date_open <= current_time,
                    Role_Listing.date_close >= current_time,
                    Role_Listing.num_opening > 0,
                )
            ).order_by(desc(Role_Listing.date_open))

            print(base_query.all())

            if role_name:
                print("filtering by name")
                # Setting a similarity threshold for search and role matching
                # Set a threshold for matching similarity
                base_query = base_query.filter(
                    Role_Listing.role_name.like(f"%{role_name}%")
                )

            if department != "Department":
                print("filtering by department")
                base_query = base_query.filter(Role_Listing.dept == department)

            print(base_query.all())

            if country != "Country":
                print("Filtering by country")
                base_query = base_query.filter(Role_Listing.country == country)

            print(base_query.all())
            #
            if recency != "Any time":
                print("Filtering by recency")
                if recency == "Past 24 hours":
                    print("Filtering by past 24 hours")
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=1)
                    )
                elif recency == "Past week":
                    print("Filtering by past week")
                    print(Role_Listing.date_open)
                    print(current_time)
                    print(current_time - timedelta(days=7))
                    print(Role_Listing.date_open >= current_time - timedelta(days=7))
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=7)
                    )
                elif recency == "Past month":
                    print("Filtering by past month")
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=30)
                    )
                else:
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=3650)
                    )

            """
            if required_skills:
                try:
                    role_required_skills = get_skills_required()
                    for skill in required_skills:

                except:
                    pass
                    """

            print(base_query.all())

            role_listings = base_query.all()
            if len(required_skills) > 0:
                print("checking if roles match required skills")
                print("yes")
                filtered_role_listings = []
                for listing in role_listings:
                    skills_required_json = get_skills_required(listing.role_name)
                    skills_required_dict = json.loads(skills_required_json.data)
                    skills_required_list = skills_required_dict["data"][
                        "skills_required"
                    ]

                    # Check if 'required_skills' is a subset of 'skills_required_list'
                    if set(required_skills).issubset(set(skills_required_list)):
                        filtered_role_listings.append(listing)

                role_listings = filtered_role_listings

            num_role_listings = len(role_listings)

            print(f"Number of role listings: {num_role_listings}")

            listings_per_page = 5

            pages_required = (
                num_role_listings + listings_per_page - 1
            ) // listings_per_page
            print(
                f"Number of pages required ({listings_per_page} listings per page): {pages_required}"
            )
            result = {
                "pages_required": pages_required,
                "num_role_listings": num_role_listings,
            }
            return result


@app.route("/design_reference")
def design_reference():
    dynamic_content = "This content is coming from Flask!"
    # Keep design reference untouched
    return render_template("design_reference.html")


@app.route("/unauthorised")
def unauthorised():
    return render_template("unauthorised.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/staff_profile")
@login_required(allowed_roles=[1, 2])
def staff_profile():
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")

    # user_name = session.get('user_name')
    print(Staff_ID)
    print(Staff_Name)
    return render_template(
        "staff_profile.html",
        Staff_Name=Staff_Name,
        Email=Email,
        Role=Role,
        Staff_Fname=Staff_Fname,
        Staff_Lname=Staff_Lname,
        Dept=Dept,
        Country=Country,
    )


@app.route("/HR_profile")
@login_required(allowed_roles=[1, 4])
def HR_profile():
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")

    # user_name = session.get('user_name')
    print(Staff_ID)
    print(Staff_Name)
    return render_template(
        "HR_profile.html",
        Staff_Name=Staff_Name,
        Email=Email,
        Role=Role,
        Staff_Fname=Staff_Fname,
        Staff_Lname=Staff_Lname,
        Dept=Dept,
        Country=Country,
    )


@app.route("/all_listings_staff/<int:page>", methods=["GET", "POST"])
@login_required(allowed_roles=[1, 2])
def all_listings_staff(page):
    print(f"Page index requested is: {page}")
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")
    print(Staff_ID)
    print(Role)
    print(Staff_Fname)
    print(Staff_Lname)
    print(Staff_Name)
    print(Dept)
    print(Country)
    print(Email)

    countries_response = get_all_countries()[0].get_json()
    if countries_response["code"] == 200:
        countries = countries_response["data"]

    print("checkpoint 11")
    departments_response = get_all_departments()[0].get_json()
    if departments_response["code"] == 200:
        departments = departments_response["data"]

    print("checkpoint 12")
    skills_response = get_all_skills()[0].get_json()
    if skills_response["code"] == 200:
        skills = skills_response["data"]

    pages_required = 1
    num_open_listings = 0
    results_per_page = 5

    offset = (page - 1) * results_per_page
    offset_end = offset + results_per_page

    try:
        # Fetch staff skills using the existing route
        # Checking if there is input search/filter

        role_search = request.form.get("role_name")
        recency = request.form.get("recency")
        country = request.form.get("country")
        department = request.form.get("department")
        required_skills = request.form.getlist("required_skills[]")

        print(f"role_search: {role_search}")
        print(f"recency: {recency}")
        print(f"country: {country}")
        print(f"department: {department}")
        print(f"required_skills: {required_skills}")

        search = False
        if role_search or recency or country or department or required_skills:
            print("ROLE SEARCH")
            search = True
        print("Checkpoint 1")
        staff_skills_json = get_skills()[0].get_json()
        print(staff_skills_json)
        staff_skills_dict = staff_skills_json.get("data", {})
        print(staff_skills_dict)
        skill_names = staff_skills_dict.get("skill_names", [])
        descriptions = staff_skills_dict.get("descriptions", [])
        # staff_skills_set = set(staff_skills_json.get('data', []))
        paired_skills = list(zip(skill_names, descriptions))
        print(paired_skills)

        if search:
            #IF THERE IS INPUT SEARCH
            page = 1
            search_params = {
                "role_search": role_search,
                "recency": recency,
                "country": country,
                "department": department,
                "required_skills": required_skills,
            }

            if role_search != None:
                session["role_search"] = None
            else:
                session["role_search"] = role_search

            if recency == "Any time":
                session["recency"] = None
            else:
                session["recency"] = recency

            if country == "Country":
                session["country"] = None
            else:
                session["country"] = country

            if department == "Department":
                session["department"] = None
            else:
                session["department"] = department

            if required_skills == []:
                session["required_skills"] = None
            else:
                session["required_skills"] = required_skills

            print(f"role search session: {session['role_search']}")
            print(f"recency session: {session['recency']}")
            print(f"country session: {session['country']}")
            print(f"department session: {session['department']}")
            print(f"required_skills session: {session['required_skills']}")

            listings_json = get_all_open_role_listings(
                search_params, offset=offset, limit=results_per_page
            )
            results = calculate_num_listings(search_params)
            print(f"results: {results}")
            pages_required = results["pages_required"]
            num_open_listings = results["num_role_listings"]
        else:
            #IF THERE IS NOT INPUT SEARCH
            listings_json = get_all_open_role_listings(
                False, offset=offset, limit=results_per_page
            )
            print(len(listings_json[0].get_json()["data"]))
            results = calculate_num_listings(None)
            pages_required = results["pages_required"]
            num_open_listings = results["num_role_listings"]
            print(num_open_listings)

        try:
            #IF THERE ARE LISTING RESULTS
            listings_dict = listings_json[0].get_json()
            listings = []
            if listings_dict:
                data = listings_dict["data"]
                for listing in data:
                    print("--------------GETTING DETAILS FOR LISTING--------------")
                    date_open = listing["date_open"]
                    input_open_datetime = datetime.strptime(
                        date_open, "%Y-%m-%dT%H:%M:%S"
                    )
                    date_close = listing["date_close"]
                    input_close_datetime = datetime.strptime(
                        date_close, "%Y-%m-%dT%H:%M:%S"
                    )
                    if (
                        input_open_datetime < datetime.now()
                        and input_close_datetime > datetime.now()
                        and listing["num_opening"] > 0
                    ):
                        status = "Open"
                    else:
                        status = "Closed"
                    manager_json = get_staff_details(listing["reporting_mng"])
                    manager_dict = json.loads(manager_json.data)
                    manager_name = (
                        manager_dict["data"]["staff_fname"]
                        + " "
                        + manager_dict["data"]["staff_lname"]
                    )
                    manager_dept = manager_dict["data"]["dept"]
                    role_desc_json = get_role_description(listing["role_name"])
                    role_desc_dict = json.loads(role_desc_json.data)
                    role_desc = role_desc_dict["data"]
                    skills_required_json = get_skills_required(listing["role_name"])
                    skills_required_dict = json.loads(skills_required_json.data)
                    skills_required_list = skills_required_dict["data"]["skills_required"]

                    print("SKILLS REQUIRED LIST FOR THE ROLE")
                    print(skills_required_list)

                    print("SKILLS THAT THE STAFF POSSESS")
                    staff_skills_list = staff_skills_dict['skill_names']


                    matched_skills = list(set(staff_skills_list) & set(skills_required_list))
                    print("MATCHED SKILLS LIST")
                    print(matched_skills)

                    # Calculate matched and unmatched skills for each listing
                    matched_skills = set(skills_required_list) & set(paired_skills)
                    print(matched_skills)
                    unmatched_skills = set(skills_required_list) - matched_skills
                    print(unmatched_skills)
                    print("debug17")
                    listingData = {
                        "role_name": listing["role_name"],
                        "date_open": input_open_datetime.strftime("%d/%m/%Y"),
                        "date_close": input_close_datetime.strftime("%d/%m/%Y"),
                        "dept": listing["dept"],
                        "country": listing["country"],
                        "num_opening": listing["num_opening"],
                        "listing_id": listing["listing_id"],
                        "manager_name": manager_name,
                        "manager_dept": manager_dept,
                        "status": status,
                        "role_desc": role_desc,
                        "skills_required_list": skills_required_list,
                        "matched_skills": list(
                            matched_skills
                        ),  # Include matched skills
                        "unmatched_skills": list(
                            unmatched_skills
                        ),  # Include unmatched skills
                    }
                    print(listingData)
                    listings.append(listingData)
                    num_results = len(listings)
                    print("num_results" + str(num_results))

            else:
                print("0 results")
                pass

            print("debug9")
            print(f"pages required: {pages_required}")

            session_role_search = session.get("role_search")
            session_recency = session.get("recency")
            session_country = session.get("country")
            session_department = session.get("department")
            session_required_skills = session.get("required_skills")

            print(f"session_role_search: {session_role_search}")
            print(f"session_recency: {session_recency}")
            print(f"session_country: {session_country}")
            print(f"session_department: {session_department}")
            print(f"session_required_skills: {session_required_skills}")

            if offset_end >= num_open_listings:
                print("offset_end greater than total")
                offset_end = num_open_listings

            print("gonna print listings")
            pages_required = int(pages_required)
            print(pages_required)
            return render_template(
                "all_listings_staff.html",
                listings=listings,
                num_results=num_results,
                Staff_Name=Staff_Name,
                countries=countries,
                departments=departments,
                skills=skills,
                pages_required=pages_required,
                current_page=page,
                session_role_search=session_role_search,
                session_recency=session_recency,
                session_country=session_country,
                session_department=session_department,
                session_required_skills=session_required_skills,
                offset=offset + 1,
                offset_end=offset_end,
                num_role_listings=num_open_listings,
            )
        except:
            print("reached exception")
            session_role_search = session.get("role_search")
            session_recency = session.get("recency")
            session_country = session.get("country")
            session_department = session.get("department")
            session_required_skills = session.get("required_skills")
        
            if offset_end >= num_open_listings:
                print("offset_end greater than total")
                offset_end = num_open_listings

            return render_template(
                "all_listings_staff.html",
                num_results="0",
                countries=countries,
                departments=departments,
                skills=skills,
                Staff_Name=Staff_Name,
                pages_required=pages_required,
                current_page=page,
                session_role_search=session_role_search,
                session_recency=session_recency,
                session_country=session_country,
                session_department=session_department,
                session_required_skills=session_required_skills,
                offset=offset,
                offset_end=offset_end,
                num_role_listings=num_open_listings,
            )
    except Exception as e:
        # Handle exceptions (e.g., network errors) here
        print(traceback.format_exc())
        return str(e), 500  # Return an error response with a 500 status code


@app.route('/get_all_open_role_listings', methods=["GET"])
# @login_required(allowed_roles=[1,2,3,4])
def get_all_open_role_listings(search, offset, limit):
    from db_config.models import Role_Listing
    try:
        # Scenario where there is input search & filter
        if search:
         
            role_name = search["role_search"]
            recency = search["recency"]
            country = search["country"]
            department = search["department"]
            required_skills = search["required_skills"]
        

            current_time = datetime.now()
        
            base_query = Role_Listing.query.filter(
                and_(
                    Role_Listing.date_open <= current_time,
                    Role_Listing.date_close >= current_time,
                    Role_Listing.num_opening > 0,
                )
            ).order_by(desc(Role_Listing.date_open))
    
            if role_name:
      
                base_query = base_query.filter(
                    Role_Listing.role_name.like(f"%{role_name}%")
                )

            if department != "Department":

                base_query = base_query.filter(Role_Listing.dept == department)


            if country != "Country":

                base_query = base_query.filter(Role_Listing.country == country)

            if recency != "Any time":
                if recency == "Past 24 hours":
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=1)
                    )
                elif recency == "Past week":

                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=7)
                    )
                elif recency == "Past month":

                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=30)
                    )
                else:
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=3650)
                    )

            """
            if required_skills:
                try:
                    role_required_skills = get_skills_required()
                    for skill in required_skills:

                except:
                    pass
                    """


            role_listings = base_query.all()
 
            print(len(role_listings))
            if len(required_skills) > 0:
       
                filtered_role_listings = []
                for listing in role_listings:
                    skills_required_json = get_skills_required(listing.role_name)
                    skills_required_dict = json.loads(skills_required_json.data)
                    skills_required_list = skills_required_dict["data"][
                        "skills_required"
                    ]

                    # Check if 'required_skills' is a subset of 'skills_required_list'
                    if set(required_skills).issubset(set(skills_required_list)):
                        filtered_role_listings.append(listing)

                role_listings = filtered_role_listings

            if len(role_listings) > 0:
                print(len(role_listings))
                return (
                    jsonify(
                        {
                            "code": 200,
                            "data": [listing.json() for listing in role_listings],
                        }
                    ),
                    200,
                )
            else:
      
                return (
                    jsonify({"code": 404, "data": "There are no role listings",}),
                    404,
                )

        # Scenario where there isn't input search & filter
        else:
       

            current_time = datetime.now()
            role_listings = (
                Role_Listing.query.filter(
                    and_(
                        Role_Listing.date_open <= current_time,
                        Role_Listing.date_close >= current_time,
                        Role_Listing.num_opening > 0,
                        Role_Listing.date_close >= current_time,
                    )
                )
                .order_by(desc(Role_Listing.date_open))
                .offset(offset)
                .limit(limit)
                .all()
            )


            if len(role_listings) > 0:
               
                return (
                    jsonify(
                        {
                            "code": 200,
                            "data": [listing.json() for listing in role_listings],
                        }
                    ),
                    200,
                )
            else:
                return jsonify({"code": 404, "data": "There are no role listings"}), 404

    except Exception as e:
        db.session.rollback()
      
        return jsonify({"code": 500, "data": str(e)}), 500


@app.route("/calculate_pages_required_all_HR")
def calculate_pages_required_all_HR(search):
    from db_config.models import Role_Listing
    if search == None:
        listings_per_page = 8
        role_listings = Role_Listing.query.all()
 
        num_role_listings = len(role_listings)

        pages_required = (
            num_role_listings + listings_per_page - 1
        ) // listings_per_page
        print(num_role_listings)
        print(pages_required)
        return {
            "pages_required": pages_required,
            "num_role_listings": num_role_listings,
            "role_listings": role_listings
        }
    else:
        listings_per_page = 8
        status = search["status"]
        role_name = search["role_search"]
        recency = search["recency"]
        country = search["country"]
        if country == None:
            country = "Country"
        department = search["department"]
        required_skills = search["required_skills"]

        base_query = Role_Listing.query.filter()

        current_time = datetime.now()

        if status != "Status":
       
            if status == "Open":
                base_query = Role_Listing.query.filter(
                    and_(
                        Role_Listing.date_open <= current_time,
                        Role_Listing.date_close >= current_time,
                        Role_Listing.num_opening > 0,
                    )
                )
            elif status == "Closed":
                base_query = Role_Listing.query.filter(
                    or_(
                        Role_Listing.date_open > current_time,
                        Role_Listing.date_close < current_time,
                        Role_Listing.num_opening == 0,
                    )
                )

        if role_name:
    
            # Setting a similarity threshold for search and role matching
            # Set a threshold for matching similarity
            base_query = base_query.filter(
                Role_Listing.role_name.like(f"%{role_name}%")
            )

        if department != "Department":
         
            base_query = base_query.filter(Role_Listing.dept == department)

        if country != "Country":
      
            base_query = base_query.filter(Role_Listing.country == country)

        if recency != "Any time":
      
            if recency == "Past 24 hours":
             
                base_query = base_query.filter(
                    Role_Listing.date_open >= current_time - timedelta(days=1)
                )
            elif recency == "Past week":
            
                base_query = base_query.filter(
                    Role_Listing.date_open >= current_time - timedelta(days=7)
                )
            elif recency == "Past month":
             
                base_query = base_query.filter(
                    Role_Listing.date_open >= current_time - timedelta(days=30)
                )
            else:
                base_query = base_query.filter(
                    Role_Listing.date_open >= current_time - timedelta(days=3650)
                )

        role_listings = base_query.all()
        num_role_listings = len(role_listings)

        pages_required = (
            num_role_listings + listings_per_page - 1
        ) // listings_per_page
     
        return {
            "pages_required": pages_required,
            "num_role_listings": num_role_listings,
            "role_listings": role_listings
        }

@app.route('/get_all_listings', methods=["GET"])
@login_required(allowed_roles=[3,4])
def get_all_listings_route():
    data = request.json
    search = data.get('search', None)
    offset = data.get('offset', 0)
    limit = data.get('limit', 8)
    return get_all_listings(search, offset, limit)

def get_all_listings(search, offset, limit):
    from db_config.models import Role_Listing
    try:
        # Scenario where there is input search & filter
        if search:
            status = search["status"]
            role_name = search["role_search"]
            recency = search["recency"]
            country = search["country"]
            if country == None:
                country = "Country"
            department = search["department"]
            required_skills = search["required_skills"]
            print("checkpoint1")
            base_query = Role_Listing.query.filter().order_by(desc(Role_Listing.date_open))

            print("checkpoint2")
            current_time = datetime.now()
            if status != "Status":
                print("Filtering by status")
                if status == "Open":
                    base_query = Role_Listing.query.filter(
                        and_(
                            Role_Listing.date_open <= current_time,
                            Role_Listing.date_close >= current_time,
                            Role_Listing.num_opening > 0,
                        )
                    )
                elif status == "Closed":
                    base_query = Role_Listing.query.filter(
                        or_(
                            Role_Listing.date_open > current_time,
                            Role_Listing.date_close < current_time,
                            Role_Listing.num_opening == 0,
                        )
                    )

            if role_name:
                print("filtering by name")
                # Setting a similarity threshold for search and role matching
                # Set a threshold for matching similarity
                base_query = base_query.filter(
                    Role_Listing.role_name.like(f"%{role_name}%")
                )

            print("results after query by name")
            print(base_query.all())

            if department != "Department":
                print("filtering by department")
                base_query = base_query.filter(Role_Listing.dept == department)

            print("results after query by department")
            print(base_query.all())

            
            if country != "Country":
                print("Filtering by country")
                print(country)
                print(Role_Listing.country)
                base_query = base_query.filter(Role_Listing.country == country)
                

            print("results after query by country")
            print(base_query.all())

            if recency != "Any time":
                print("Filtering by recency")
                if recency == "Past 24 hours":
                    print("Filtering by past 24 hours")
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=1)
                    )
                elif recency == "Past week":
                    print("Filtering by past week")
                    print(Role_Listing.date_open)
                    print(current_time)
                    print(current_time - timedelta(days=7))
                    print(Role_Listing.date_open >= current_time - timedelta(days=7))
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=7)
                    )
                elif recency == "Past month":
                    print("Filtering by past month")
                    base_query = base_query.filter(
                        Role_Listing.date_open >= current_time - timedelta(days=30)
                    )
                else:
                    base_query = base_query.filter(Role_Listing.date_open >= current_time - timedelta(days=3650))
            
            print("checkpoint3")
            role_listings = base_query.order_by(desc(Role_Listing.date_open)).offset(offset).limit(limit).all()
            print("checkpoint4")
            if len(role_listings) > 0:
                print("checkpoint5")
                print(len(role_listings))
                return (
                    jsonify(
                        {
                            "code": 200,
                            "data": [listing.json() for listing in role_listings],
                        }
                    ),
                    200,
                )
            else:
                print("no such listing")
                return (
                    jsonify({"code": 404, "message": "There are no role listings",}),
                    404,
                )
        else:
            print(f"Requested offset: {offset}")
            print(f"Requested limit: {limit}")

            role_listings = (
                Role_Listing.query.order_by(desc(Role_Listing.date_open))
                .offset(offset)
                .limit(limit)
                .all()
            )
            print("checkpoint7")
            if len(role_listings) > 0:
                print("checkpoint8")
                print(len(role_listings))
                return (
                    jsonify(
                        {
                            "code": 200,
                            "data": [listing.json() for listing in role_listings],
                        }
                    ),
                    200,
                )
            else:
                print("checkpoint9")
                return (
                    jsonify({"code": 404, "message": "There are no role listings"}),
                    404,
                )

    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({
            "code": 500,
            "error": str(e)
            }), 500


@app.route("/view_a_listing/<int:listing_id>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def view_a_listing(listing_id):
    try:
        # Check if the listing exists
        listing = Role_Listing.query.filter_by(listing_id=listing_id).first()
        if not listing:
            return jsonify({"error": "Role listing not found"}), 404
        else:
            return jsonify({"code": 200, "data": listing.json()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/all_skills")
def all_skills():
    try:
        skills = Skill.query.filter().all()
        if len(skills) > 0:
            return jsonify({"code": 200, "data": [skill.json() for skill in skills]})
        else:
            return jsonify({"code": 404, "message": "There are no skills"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/skills")
# @login_required(allowed_roles=[1,2,3,4])
def get_skills():
    try:
        from db_config.models import Staff
        from db_config.models import Skill
        staff_id = session.get("Staff_ID")
        # staff_id = 140002
        # Check if staff exists
        staff = Staff.query.filter_by(staff_id=staff_id).first()
        print(staff)
        if not staff:
            return jsonify({"code": 404, "data": "Staff does not exist"}), 404

        # Staff is found, get staff_skills
        staff_details = staff.json()
        staff_skills = staff_details.get("staff_skills", [])

        if len(staff_skills) == 0:
            return jsonify({"code": 404, "data": "You do not possess any skills."}), 404

        skills = [skill.get("skill_name") for skill in staff_skills]

        # Get skill description
        desc_list = [
            Skill.query.filter_by(skill_name=name).first().json().get("skill_desc", [])
            for name in skills
        ]

        return (
            jsonify(
                {
                    "code": 200,
                    "data": {"skill_names": skills, "descriptions": desc_list},
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "code": 500}), 500


@app.route("/listings")
@login_required(allowed_roles=[1, 2, 3, 4])
def listings():
    dynamic_content = "This content is coming from Flask!"
    return render_template("listings.html")


@app.route("/applied_roles_staff")
@login_required(allowed_roles=[1, 2, 3, 4])
def applied_roles():
    # dynamic_content = "This content is coming from Flask!"
    # return render_template("applied_roles.html")
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")

    # user_name = session.get('user_name')
    print(Staff_ID)
    print(Staff_Name)
    return render_template(
        "applied_roles.html",
        Staff_Name=Staff_Name,
        Email=Email,
        Role=Role,
        Staff_Fname=Staff_Fname,
        Staff_Lname=Staff_Lname,
        Dept=Dept,
        Country=Country,
    )


@app.route("/role_creation")
@login_required(allowed_roles=[1, 2, 3, 4])
def role_creation():
    user_id = session.get("user_id")
    user_name = session.get("user_name")
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")
    print(user_id)
    print(user_name)
    dynamic_content = "This content is coming from Flask!"
    return render_template(
        "role_creation.html",
        Staff_Name=Staff_Name,
        Email=Email,
        Role=Role,
        Staff_Fname=Staff_Fname,
        Staff_Lname=Staff_Lname,
        Dept=Dept,
        Country=Country,
    )


@app.route("/edit_role/<int:listing_id>")
@login_required(allowed_roles=[1, 4])
def edit_role(listing_id):
    # Get the listing information
    json_data = get_listing(listing_id)
    return render_template("edit_role.html", json_data=json_data)


@app.route("/role_search", methods=["GET", "POST"])
@login_required(allowed_roles=[1, 2, 3, 4])
def role_search():
    role_search = request.form["role_name"]
    recency = request.form["recency"]
    country = request.form["country"]
    department = request.form["department"]
    required_skills = request.form.getlist("required_skills[]")
    print(role_search)
    print(recency)
    print(country)
    print(department)
    print(required_skills)
    return "role_search"


@app.route("/login", methods=["GET", "POST"])
def login():
    user_id = session.get("user_id")
    user_name = session.get("user_name")
    print(user_id)
    print(user_name)
    input_id = request.form.get("ID")
    print(input_id)
    if not input_id:
        return render_template("login.html")

    try:
        input_id = int(input_id)
    except ValueError:
        return render_template("login.html")

    print("performing user ID lookup")
    staff = Staff.query.filter_by(staff_id=input_id).first()

    if staff:
        session["Staff_ID"] = staff.staff_id
        session["Role"] = staff.role
        print("role is", staff.role)
        session["Staff_Fname"] = staff.staff_fname
        session["Staff_Lname"] = staff.staff_lname
        session["Staff_Name"] = f"{staff.staff_fname} {staff.staff_lname}"
        session["Dept"] = staff.dept
        session["Country"] = staff.country
        session["Email"] = staff.email

        if staff.role == 2:
            print("role is staff")
            return redirect(url_for("all_listings_staff", page=1))
        elif staff.role == 4:
            print("role is HR")
            return redirect(url_for("all_listings_HR", page=1))
        elif staff.role == 1:
            print("role is Admin")
            return redirect(url_for("all_listings_HR", page=1))
    else:
        print("User not found")

    dynamic_content = "This content is coming from Flask!"
    return render_template("login.html")


@app.route("/all_listings_HR/<int:page>", methods=["GET", "POST"])
@login_required(allowed_roles=[1, 4])
def all_listings_HR(page):
    print(f"page requested {page}")

    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")
    print(Staff_ID)
    print(Role)
    print(Staff_Fname)
    print(Staff_Lname)
    print(Staff_Name)
    print(Dept)
    print(Country)
    print(Email)

    pages_required = 1
    num_open_listings = 0
    results_per_page = 8

    offset = (page - 1) * results_per_page
    offset_end = offset + results_per_page

    countries_response = get_all_countries()[0].get_json()
    if countries_response["code"] == 200:
        countries = countries_response["data"]

    departments_response = get_all_departments()[0].get_json()
    if departments_response["code"] == 200:
        departments = departments_response["data"]

    skills_response = get_all_skills()[0].get_json()
    if skills_response['code'] == 200:
        skills = skills_response['data']

    try:
        # Checking if there is input search/filter
        status = request.form.get("status")
        role_search = request.form.get("role_name")
        recency = request.form.get("recency")
        country = request.form.get("country")
        department = request.form.get("department")
        required_skills = request.form.getlist("required_skills[]")
        # print(user_id)
        # print(user_name)

        # print(status)
        # print(role_search)
        # print(recency)
        # print(country)
        # print(department)
        # print(required_skills)

        search = False
        if status or role_search or recency or country or department or required_skills:
            search = True

        session_role_search = None
        session_status = None
        session_recency = None
        session_country = None
        session_department = None
        session_required_skills = None

        if search:
            print("--------------USER MADE A SEARCH--------------")
            page = 1
            session["existing_search"] = True
            search_params = {
                "role_search": role_search,
                "status": status,
                "recency": recency,
                "country": country,
                "department": department,
                "required_skills": required_skills,
            }

            if role_search == None:
                session["role_search"] = None
            else:
                session["role_search"] = role_search
                session_role_search = role_search

            if status == "Status":
                session["status"] = None
            else:
                session["status"] = status
                session_status = status

            if recency == "Any time":
                session["recency"] = None
            else:
                session["recency"] = recency
                session_recency = recency

            if country == "Country":
                session["country"] = None
            else:
                session["country"] = country
                session_country = country

            if department == "Department":
                session["department"] = None
            else:
                session["department"] = department
                session_department = department

            if required_skills == []:
                session["required_skills"] = None
            else:
                session["required_skills"] = required_skills
                session_required_skills = required_skills

            print(f"role search session: {session['role_search']}")
            print(f"recency session: {session['recency']}")
            print(f"country session: {session['country']}")
            print(f"department session: {session['department']}")
            print(f"required_skills session: {session['required_skills']}")

            search_params = {
                "role_search": role_search,
                "status": status,
                "recency": recency,
                "country": country,
                "department": department,
                "required_skills": required_skills,
            }
            print(f"search param: {search_params}")
            results = calculate_pages_required_all_HR(search_params)
            pages_required = results["pages_required"]
            num_role_listings = results["num_role_listings"]
            print(f"----------{num_role_listings} RESULTS FOR SEARCH---------------")
            print(f"---------PAGINATION REQUIRED: {pages_required}----------------")
            listings_json = get_all_listings(search_params, offset=offset, limit=results_per_page)
            print(listings_json)

        elif session.get("existing_search"):
            print("-------------USER CLICKED BEYOND PAGE 1 FOR EXISTING SEARCH---------------")
            role_search = session["role_search"]
            status = session["status"]
            recency = session["recency"]
            country = session["country"]
            department = session["department"]
            required_skills = session["required_skills"]
            session_role_search = role_search
            session_status = status
            session_recency = recency
            session_country = country
            session_department = department
            session_required_skills = required_skills

            search_params = {
                "role_search": role_search,
                "status": status,
                "recency": recency,
                "country": country,
                "department": department,
                "required_skills": required_skills,
            }

            results = calculate_pages_required_all_HR(search_params)
            pages_required = results["pages_required"]
            num_role_listings = results["num_role_listings"]
            print(f"----------{num_role_listings} RESULTS FOR SEARCH---------------")
            print(f"---------PAGINATION REQUIRED: {pages_required}----------------")
            listings_json = get_all_listings(
                search_params, offset=offset, limit=results_per_page
            )
            print(listings_json)

        else:
            print("-------------SEARCHING FOR ALL RESULTS W/O FILTERS---------------")
            session["preexisting_search"] = False
            results = calculate_pages_required_all_HR(None)
            pages_required = results["pages_required"]
            num_role_listings = results["num_role_listings"]
            print(f"----------{num_role_listings} RESULTS FOR SEARCH---------------")
            print(f"------------PAGINATION REQUIRED: {pages_required}--------------")
            listings_json = get_all_listings(False, offset=offset, limit=results_per_page)
            print(listings_json)

        listings_dict = listings_json[0].get_json()
        listings = []
        if listings_dict["code"] == 200:
            print("checkpoint 4")
            data = listings_dict["data"]
            for listing in data:
                print("-------------OBTAINING DETAILS FOR RESULT ROLE LISTING----------------")
                print("checkpoint 5")
                print(listing['listing_id'])
                num_applicants = get_num_applicants_by_listing(listing['listing_id'])
                print("checkpoint 5.1")
                date_open = listing['date_open']
                input_open_datetime = datetime.strptime(date_open, "%Y-%m-%dT%H:%M:%S")
                date_close = listing["date_close"]
                input_close_datetime = datetime.strptime(
                    date_close, "%Y-%m-%dT%H:%M:%S"
                )

                print("checkpoint 6")
                if (
                    input_open_datetime < datetime.now()
                    and input_close_datetime > datetime.now()
                    and listing["num_opening"] > 0
                ):
                    status = "Open"
                else:
                    status = "Closed"
                print("checkpoint 7")
                manager_json = get_staff_details(listing["reporting_mng"])
                manager_dict = json.loads(manager_json.data)
                manager_name = (
                    manager_dict["data"]["staff_fname"]
                    + " "
                    + manager_dict["data"]["staff_lname"]
                )
                manager_dept = manager_dict["data"]["dept"]

                print("checkpoint 8")
                role_desc_json = get_role_description(listing["role_name"])
                role_desc_dict = json.loads(role_desc_json.data)
                role_desc = role_desc_dict["data"]

                skills_required_json = get_skills_required(listing["role_name"])
                skills_required_dict = json.loads(skills_required_json.data)
                skills_required_list = skills_required_dict["data"]["skills_required"]

                print("checkpoint 9")
                listingData = {
                    "role_name": listing["role_name"],
                    "date_open": input_open_datetime.strftime("%d/%m/%Y"),
                    "date_close": input_close_datetime.strftime("%d/%m/%Y"),
                    "dept": listing["dept"],
                    "country": listing["country"],
                    "num_opening": listing["num_opening"],
                    "num_applicants": num_applicants,
                    "listing_id": listing["listing_id"],
                    "manager_name": manager_name,
                    "manager_dept": manager_dept,
                    "status": status,
                    "role_desc": role_desc,
                    "skills_required_list": skills_required_list,
                }
                listings.append(listingData)
                num_results = len(listings)
                print("num_results", num_results)
            
            if offset_end > num_role_listings:
                offset_end = num_role_listings
                
            return render_template("all_listings_HR.html", 
                                   listings=listings,
                                   num_results=num_results,
                                   Staff_Name=Staff_Name,
                                   countries=countries,
                                   departments=departments,
                                   skills=skills,
                                   pages_required=pages_required,   
                                   num_role_listings=num_role_listings,
                                   offset = offset + 1,
                                   offset_end = offset_end,
                                   current_page = page,
                                   session_role_search = session_role_search,
                                   session_recency = session_recency,
                                   session_status = session_status,
                                   session_country = session_country,
                                   session_department = session_department,
                                   session_required_skills = session_required_skills
                                   )
        else:
            if offset_end > num_role_listings:
                offset_end = num_role_listings
            return render_template("all_listings_HR.html",
                                   countries=countries,
                                   departments=departments,
                                   Staff_Name=Staff_Name,
                                   skills=skills,
                                   pages_required=1,
                                   num_role_listings=0,
                                   offset=0,
                                   offset_end=0,
                                   current_page=1,
                                   session_role_search=session_role_search,
                                   session_recency=session_recency,
                                   session_status=session_status,
                                   session_country=session_country,
                                   session_department=session_department,
                                   session_required_skills=session_required_skills)
    except Exception as e:
        # Handle exceptions (e.g., network errors) here
        print(traceback.format_exc())
        print("here error")
        return str(e), 500  # Return an error response with a 500 status code


@app.route("/all_applicants_HR", methods=["GET", "POST"])
@login_required(allowed_roles=[1, 4])
def all_applicants_HR():
    user_id = session.get("user_id")
    user_name = session.get("user_name")
    Staff_ID = session.get("Staff_ID")
    Role = session.get("Role")
    Staff_Fname = session.get("Staff_Fname")
    Staff_Lname = session.get("Staff_Lname")
    Staff_Name = session.get("Staff_Name")
    Dept = session.get("Dept")
    Country = session.get("Country")
    Email = session.get("Email")
    print(user_id)
    print(user_name)

    countries_response = requests.get("http://127.0.0.1:5500/get_all_countries")
    if countries_response.status_code == 200:
        countries_data = countries_response.json()
        countries = countries_data.get("countries")

    departments_response = requests.get("http://127.0.0.1:5500/get_all_departments")
    if departments_response.status_code == 200:
        departments_data = departments_response.json()
        departments = departments_data.get("departments")

    return render_template(
        "all_applicants_HR.html",
        countries=countries,
        departments=departments,
        Staff_Name=Staff_Name,
        Email=Email,
        Role=Role,
        Staff_Fname=Staff_Fname,
        Staff_Lname=Staff_Lname,
        Dept=Dept,
        Country=Country,
    )


# Define a route to get the listing ID by name
@app.route("/get_listing_id_by_name/<string:role_name>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_listing_id_by_name(role_name):
    try:
        # Query the Role_Listing table to find the listing ID by role name
        role_listing = Role_Listing.query.filter(
            Role_Listing.role_name == role_name
        ).first()
        if role_listing:
            return jsonify({"listingId": role_listing.listing_id}), 200
        else:
            return jsonify({"error": "Role listing not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# get applications of each staff
@app.route("/get_application_history", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_application_history():
    try:
        # Fetch application data for the specified staff_id
        staff_id = session.get("Staff_ID")
        print("staff_id:", staff_id)
        applications = Application.query.filter_by(staff_id=staff_id).all()

        # Create a list to store application history data
        application_history = []

        for application in applications:
            # Fetch role_listing data based on the listing_id in each application
            role_listing = Role_Listing.query.filter_by(
                listing_id=application.listing_id
            ).first()

            if role_listing:

                # Fetch staff data based on staff_id
                staff = Staff.query.get(staff_id)

                # Combine staff_fname and staff_lname to create staff_name
                staff_name = f"{staff.staff_fname} {staff.staff_lname}"

                # Append application and role_listing data to the application history list
                application_history.append(
                    {
                        "application_id": application.application_id,
                        "staff_name": staff_name,
                        "role_name": role_listing.role_name,
                        "applied_date": application.applied_date.strftime("%Y-%m-%d"),
                        "status": application.status,
                    }
                )

        return jsonify({"application_history": application_history, "code": 200}), 200

    except Exception as e:
        return jsonify({"error": str(e), "code": 500}), 500


# get applications by listing id
@app.route("/get_applications_by_listing/<int:listing_id>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_applications_by_listing(listing_id):
    try:
        # Fetch application data for the specified listing_id
        applications = Application.query.filter_by(listing_id=listing_id).all()

        # Create a list to store application data
        application_list = []

        for application in applications:
            # Fetch staff data based on staff_id
            staff = Staff.query.get(application.staff_id)

            # Combine staff_fname and staff_lname to create staff_name
            staff_name = f"{staff.staff_fname} {staff.staff_lname}"
            staff_skills = list(
                skill[0]
                for skill in db.session.query(Staff_Skill.skill_name)
                .filter_by(staff_id=application.staff_id)
                .all()
            )
            # Fetch the numeric role
            numeric_role = staff.role

            # Fetch the corresponding access control name from the AccessControl table
            access_control = Access_Control.query.filter_by(
                access_id=numeric_role
            ).first()
            access_control_name = (
                access_control.access_control_name if access_control else "Unknown"
            )

            # Append application data to the application list
            application_list.append(
                {
                    "application_id": application.application_id,
                    "staff_id": staff.staff_id,
                    "staff_name": staff_name,
                    "country": staff.country,
                    "department": staff.dept,
                    "email": staff.email,
                    "role": access_control_name,
                    "skills": staff_skills,
                    "applied_date": application.applied_date.strftime("%Y-%m-%d"),
                    "status": application.status,
                }
            )

        return jsonify({"applications": application_list, "code": 200}), 200

    except Exception as e:
        return jsonify({"error": str(e), "code": 500}), 500


def get_num_applicants_by_listing(listing_id):
    from db_config.models import Application
    # Query your database to count the number of applications for the given listing_id
    num_applicants = Application.query.filter_by(listing_id=listing_id).count()
    return num_applicants


@app.route("/apply_role/<int:listing_id>", methods=["POST"])
@login_required(allowed_roles=[1, 2])
def apply_role(listing_id):
    from db_config.models import Role_Listing
    from db_config.models import Application
    try:
        staff_id = session.get('Staff_ID')
        if staff_id is None:
            return jsonify({"error": "User not authenticated"}), 401

        status = "Pending"
        applied_date = datetime.now()

        # Check if the listing exists
        role_listing = Role_Listing.query.filter_by(listing_id=listing_id).first()
        if not role_listing:
            return jsonify({"error": "Role listing not found"}), 404

        # Check if the listing is closed (past the application deadline)
        current_datetime = datetime.now()
        if role_listing.date_open > current_datetime or role_listing.date_close < current_datetime:
            return jsonify({"error": "Role listing is closed or not yet open for applications"}), 411

        # Check if the staff member has already applied to this listing
        existing_application = Application.query.filter_by(listing_id=listing_id, staff_id=staff_id).first()
        if existing_application:
            return jsonify({"error": "You have already applied to this role"}), 400

        # Insert application details
        insert_sql = text("""
            INSERT INTO application (listing_id, staff_id, status, applied_date)
            VALUES (:listing_id, :staff_id, :status, :applied_date)
        """)

        params = {
            "listing_id": listing_id,
            "staff_id": staff_id,
            "status": status,
            "applied_date": applied_date,
        }

        result = db.session.execute(insert_sql, params)
        db.session.commit()

        # Fetch the last inserted ID using SQLAlchemy's execute method
        application_id = result.lastrowid

        return jsonify({"message": "Application submitted successfully", "application_id": application_id, "code": 201}), 201

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # Print the exception traceback
        return jsonify({"error": "An error occurred while processing your application", "code": 500}), 500


@app.route("/check_application_status/<int:listing_id>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def check_application_status(listing_id):
    try:
        staff_id = session.get("Staff_ID")
        print("Request received: listing_id =", listing_id, "staff_id =", staff_id)

        # Check if the staff member with the specified staff_id has applied with the given application_id
        application = Application.query.filter_by(
            listing_id=listing_id, staff_id=staff_id
        ).first()
        if application:
            return jsonify({"status": application.status, "code": 200}), 200
        else:
            return jsonify({"status": "not_applied", "code": 201}), 201

    except Exception as e:
        return jsonify({"error": str(e), "code": 500}), 500


# Cancel application
@app.route("/delete_application/<int:application_id>", methods=["DELETE"])
@login_required(allowed_roles=[1, 2])
def delete_application(application_id):
    try:
        # Check if the application with the specified application_id and staff_id exists
        staff_id = session.get("Staff_ID")
        application = Application.query.filter_by(
            application_id=application_id, staff_id=staff_id
        ).first()

        if application:
            # Retrieve the associated role_listing for the application
            role_listing = Role_Listing.query.filter_by(
                listing_id=application.listing_id
            ).first()

            if role_listing:
                # Check if the role_listing is past the application deadline
                current_datetime = datetime.now()
                if role_listing.date_close < current_datetime:
                    return (
                        jsonify(
                            {
                                "error": "Application cannot be deleted as it's past the deadline",
                                "code": 400,
                            }
                        ),
                        400,
                    )

                # Delete the application
                db.session.delete(application)
                db.session.commit()
                return (
                    jsonify(
                        {"message": "Application deleted successfully", "code": 200}
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "Role listing not found for the application",
                            "code": 404,
                        }
                    ),
                    404,
                )
        else:
            return jsonify({"error": "Application not found", "code": 404}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "code": 500}), 500


@app.route("/get_staff_details/<int:staff_id>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_staff_details(staff_id):
    from db_config.models import Staff
    try:
        staff = Staff.query.filter_by(staff_id=staff_id).first()
        if staff:
            return jsonify({"code": 200, "data": staff.json()})
        else:
            return jsonify({"code": 404, "message": "Staff not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/get_role_description/<string:role_name>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_role_description(role_name):
    from db_config.models import Role
    try:
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            return jsonify({"code": 200, "data": role.role_desc})
        else:
            return jsonify({"code": 404, "message": "Role not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/get_all_countries", methods=["GET"])
def get_all_countries():
    from db_config.models import Country
    try:
        countries = Country.query.all()

        if not countries:
            return jsonify({"code": 404, "data": "No countries found"}), 404

        country_list = [
            {"country": country.country, "country_name": country.country_name}
            for country in countries
        ]

        return jsonify({"code": 200, "data": country_list}), 200

    except Exception as e:
        return jsonify({"code": 500, "data": str(e)}), 500


@app.route("/get_all_departments", methods=["GET"])
def get_all_departments():
    from db_config.models import Department
    try:
        departments = Department.query.all()

        if not departments:
            return jsonify({"code": 404, "data": "No departments found"}), 404

        department_list = [department.department for department in departments]

        return jsonify({"code": 200, "data": department_list}), 200

    except Exception as e:
        return jsonify({"code": 500, "data": str(e)}), 500


@app.route("/get_skills_required/<string:role_name>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_skills_required(role_name):
    from db_config.models import Role_Skill
    try:
        skills_required = Role_Skill.query.filter_by(role_name=role_name).all()
        if len(skills_required) > 0:
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "role_name": role_name,
                        "skills_required": [
                            skill.skill_name for skill in skills_required
                        ],
                    },
                }
            )
        else:
            return jsonify({"code": 404, "message": "Skills not found"}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


@app.route("/get_all_skills", methods=["GET"])
def get_all_skills():
    from db_config.models import Skill
    try:
        skills = Skill.query.all()
        if not skills:
            return jsonify({"code": 404, "data": "No skills found"}), 404
        skill_list = []
        for skill in skills:
            skill_list.append(
                {"skill_name": skill.skill_name, "skill_desc": skill.skill_desc}
            )
        return jsonify({"code": 200, "data": skill_list}), 200
    except Exception as e:
        return jsonify({"code": 500, "data": str(e)}), 500


@app.route("/match_skills/<int:listing_id>", methods=["GET"])
# @login_required(allowed_roles=[1, 2, 3, 4])
def match_skills(listing_id):
    from db_config.models import Role_Listing
    from db_config.models import Role_Skill
    from db_config.models import Staff_Skill
    try:
        staff_id = session.get("Staff_ID")

        
        # Check if the role exists
        role_listing = Role_Listing.query.filter_by(listing_id=listing_id).first()
   
        if not role_listing:
            return jsonify({"error": "Role does not exist.", "code": "404"}), 404

        # Retrieve the role_name using the listing_id
        role_name = (
            db.session.query(Role_Listing.role_name)
            .filter_by(listing_id=listing_id)
            .scalar()
        )

        # Retrieve the role's required skills
        role_skills = set(
            skill[0]
            for skill in db.session.query(Role_Skill.skill_name)
            .filter_by(role_name=role_name)
            .all()
        )

        # Retrieve the staff's skills
        staff_skills = set(
            skill[0]
            for skill in db.session.query(Staff_Skill.skill_name)
            .filter_by(staff_id=staff_id)
            .all()
        )


        # Calculate lacking skills
        lacking_skills = role_skills - staff_skills

        # Perform skill matching logic
        matched_skills = staff_skills.intersection(role_skills)

        response_data = {
            "listing_id": listing_id,
            "role_name": role_name,
            "staff_id": staff_id,
            "matched_skills": list(matched_skills),
            "lacking_skills": list(lacking_skills),
        }

        message = None
        if not matched_skills:
            message = "You have no matching skills with this role."
        else:
            message = "You have matching skills with this role!"

        return jsonify(
            {"response_data": response_data, "message": message, "code": 200}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "code": 500}), 500


# get matching skills of each applicant
@app.route("/get_matching_skills/<int:listing_id>/<int:staff_id>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_matching_skills(listing_id, staff_id):
    try:

        # Check if the role exists
        role = Role_Listing.query.filter_by(listing_id=listing_id).first()
        if not role:
            return jsonify({"error": "Role does not exist.", "code": "404"}), 404

        # Retrieve the role_name using the listing_id
        role_name = (
            db.session.query(Role_Listing.role_name)
            .filter_by(listing_id=listing_id)
            .scalar()
        )

        # Retrieve the role's required skills
        role_skills = set(
            skill[0]
            for skill in db.session.query(Role_Skill.skill_name)
            .filter_by(role_name=role_name)
            .all()
        )

        # Retrieve the staff's skills
        staff_skills = set(
            skill[0]
            for skill in db.session.query(Staff_Skill.skill_name)
            .filter_by(staff_id=staff_id)
            .all()
        )



        # Calculate lacking skills
        lacking_skills = role_skills - staff_skills

        # Perform skill matching logic
        matched_skills = staff_skills.intersection(role_skills)

        response_data = {
            "listing_id": listing_id,
            "role_name": role_name,
            "staff_id": staff_id,
            "matched_skills": list(matched_skills),
            "lacking_skills": list(lacking_skills),
        }

        message = None
        if not matched_skills:
            message = "You have no matching skills with this role."
        else:
            message = "You have matching skills with this role!"

        return jsonify(
            {"response_data": response_data, "message": message, "code": 200}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "code": 500}), 500


# Get roles, countries and departments for role creation
@app.route("/create/get_data")
@login_required(allowed_roles=[1, 4])
def get_dept_and_countries():
    try:
        # Check roles
        role_list = Role.query.all()
        if len(role_list) == 0:
            return jsonify({"code": 404, "message": "No roles in roles list"}, 404)

        # Check countries
        country_list = Country.query.all()
        if len(country_list) == 0:
            return jsonify(
                {"code": 404, "message": "Error, no countries are found."}, 404
            )

        # Check departments
        department_list = Department.query.all()
        if len(department_list) == 0:
            return jsonify(
                {"code": 404, "message": "Error, no departments are found."}, 404
            )

        roles = [r.json().get("role_name") for r in role_list]
        countries = [c.json().get("country_name") for c in country_list]
        departments = [j.json() for j in department_list]

        # Return both departments and countries
        return jsonify(
            {
                "code": 200,
                "data": {
                    "roles": roles,
                    "countries": countries,
                    "departments": departments,
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "code": 500}), 500


# Get reporting manager given a selected department
@app.route("/get_manager/<string:country>/<string:dept>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_manager(country, dept):
    try:
        managers = Staff.query.filter(
            and_(Staff.dept == dept, Staff.country == country, Staff.role >= 3)
        ).all()

        manager_id = []
        manager_name = []
        if managers:
            for m in managers:
                fname = m.json().get("staff_fname")
                lname = m.json().get("staff_lname")
                manager_name.append(fname + " " + lname)
                manager_id.append(m.json().get("staff_id"))

            return jsonify(
                {
                    "code": 200,
                    "data": {"name_list": manager_name, "id_list": manager_id},
                }
            )
        else:
            return jsonify({"code": 404, "message": "No managers found."}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500


#
@app.route("/update/check_listing_exist/<int:id>", methods=["PUT"])
# @login_required(allowed_roles=[4])
def update_check_listing(id):
    from db_config.models import Role_Listing
    staff_id = session.get("Staff_ID")
    # Get the JSON data from the request
    json_data = request.get_json()
    print(json_data)

    name = json_data["title"]
    department = json_data["department"]
    country = json_data["country"]
    start_date = json_data["startDate"]
    end_date = json_data["endDate"]
    manager = json_data["manager"]
    vacancy = json_data["vacancy"]

  
    currListing = Role_Listing.query.filter_by(listing_id=id).first()

    if not currListing:
        return jsonify({"code": 404, "message": "Listing does not exist"}), 404

    try:
        currListing.role_name = name
        currListing.dept = department
        currListing.country = country
        currListing.date_open = start_date
        currListing.date_close = end_date
        currListing.reporting_mng = manager
        currListing.num_opening = vacancy
        db.session.commit()

    except Exception as e:
        return jsonify({"code": 500, "error": str(e)}), 500

    return (
        jsonify(
            {
                "code": 201,
                "data": currListing.json(),
                "message": "Listing successfully edited! Refresh page to view.",
            }
        ),
        201,
    )


@app.route("/create/check_listing_exist", methods=["POST"])
def check_listing():
    from db_config.models import Role_Listing
    # Get the JSON data from the request
    json_data = request.get_json()

    name = json_data["title"]
    department = json_data["department"]
    country = json_data["country"]
    start_date = json_data["startDate"]
    end_date = json_data["endDate"]
    manager = json_data["manager"]
    vacancy = json_data["vacancy"]


    matching_listings = Role_Listing.query.filter(
        and_(
            Role_Listing.role_name == name,
            Role_Listing.dept == department,
            Role_Listing.country == country,
            Role_Listing.date_close >= start_date,
        )
    ).all()

    if matching_listings:
    
        return (
            jsonify(
                {
                    "code": 400,
                    "message": "Listing cannot be created. An active listing exists!",
                }
            ),
            400,
        )

    else:
        listing = Role_Listing(
            country, department, vacancy, start_date, end_date, name, manager
        )
        try:
            db.session.add(listing)
            db.session.commit()
        except Exception as e:
            return jsonify({"code": 500, "error": str(e)}), 500

        return (
            jsonify(
                {
                    "code": 201,
                    "data": listing.json(),
                    "message": "New listing created successfully!",
                }
            ),
            201,
        )


@app.route("/get_required_skills_for_role/<string:role_name>", methods=["GET"])
@login_required(allowed_roles=[1, 2, 3, 4])
def get_required_skills_for_roles(role_name):
    # Assuming you have a RoleSkill model for the role_skill table
    skills = Role_Skill.query.filter_by(role_name=role_name).all()

    if not skills:
        return jsonify({"message": "Role not found"}), 404

    skill_names = [skill.skill_name for skill in skills]
    return jsonify({"role_name": role_name, "skills": skill_names})


@app.route("/get_listing_by_id/<int:listing_id>")
# @login_required(allowed_roles=[1, 2, 3, 4])
def get_listing(listing_id):
    from db_config.models import Role_Listing
    try:
        # Check if listing if exists
        listing = Role_Listing.query.filter_by(listing_id=listing_id).first()
        if not listing:
            return {"code": 404, "message": "Listing does not exist"}, 404

        # Get listing details
        listing_details = listing.json()

        return {"code": 200, "data": listing_details}, 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5500, debug=True)

