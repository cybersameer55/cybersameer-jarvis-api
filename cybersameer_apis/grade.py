"""
@api /grade
@method GET
@param marks, max_marks
@usage /grade?key=YOUR_API_KEY&marks=85&max_marks=100
"""
from flask import Blueprint, request
from core import check_access, send_response

grade_bp = Blueprint("grade", __name__)

@grade_bp.route("/grade")
def grade():
    key       = request.args.get("key","")
    marks     = request.args.get("marks","")
    max_marks = request.args.get("max_marks","100")
    user, err = check_access(key)
    if err: return err
    if not marks: return send_response("error",{},{"message":"marks required"})
    try:
        m=float(marks); mx=float(max_marks)
        pct = m/mx*100
        if pct>=90:   grade="A+"; gpa=4.0; status="Outstanding"
        elif pct>=80: grade="A";  gpa=3.7; status="Excellent"
        elif pct>=70: grade="B+"; gpa=3.3; status="Very Good"
        elif pct>=60: grade="B";  gpa=3.0; status="Good"
        elif pct>=50: grade="C";  gpa=2.0; status="Average"
        elif pct>=40: grade="D";  gpa=1.0; status="Below Average"
        else:         grade="F";  gpa=0.0; status="Fail"
        return send_response("success",{
            "marks":m,"max_marks":mx,"percentage":round(pct,2),
            "grade":grade,"gpa":gpa,"status":status
        },{"user":user["name"]})
    except: return send_response("error",{},{"message":"Invalid numbers"})
