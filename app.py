from bson.objectid import ObjectId
import pymongo
client =pymongo.MongoClient("mongodb+srv://ryan:ryan1234@mycluster.rf6tx9u.mongodb.net/?retryWrites=true&w=majority&appName=MyCluster")
gold_db=client.goldbuysell
gold_collection=gold_db.gold
member_db=client.member_system
member_collection=member_db.users
print("資料庫連線成功")


from flask import *
app=Flask(__name__)
app.secret_key="1234"

from datetime import datetime

#主畫面
@app.route("/")
def main():
    return render_template("first.html")

#登入
@app.route("/signin",methods=["GET","POST"])
def signin():
    email=request.form.get("email")
    password=request.form.get("password")
    #!!!!!!!
    print("email:", email)
    print("password:", password)
    result=member_collection.find_one({
       "$and":[
           {"email":email},
           {"password":password}
       ]
    })
    if result==None:
        return redirect ("/error?msg=信箱或密碼錯誤")
    session["nickname"]=result["nickname"]
    return redirect("/homescreen")

#signin->signup
@app.route("/change")
def change():
    return render_template("signup.html")
                            
#註冊帳號
@app.route("/signup",methods=["GET","POST"])
def signup():
    nickname=request.form.get("nickname")
    email=request.form.get("email")
    password=request.form.get("password")
    result=member_collection.find_one({
        "$or":[
            {"nickname":nickname},
            { "email":email}           
            ]  
    })
    if result !=None:
        return redirect("/error?msg=信箱已被使用")
    member_collection.insert_one({
        "nickname":nickname,
        "email":email,
        "password":password
    })
    return render_template("signupsuccess.html")

#錯誤
@app.route("/error")
def error():
    message=request.args.get("msg","出現未知的錯誤")
    return render_template("error.html",message=message)

#登出
@app.route("/signout")
def signout():
    session.pop("nickname",None)
    return redirect("/")


#首頁
@app.route("/homescreen",methods=["GET","POST"])
def home():
    if "nickname" not in session:
        return redirect("/")
    #平均買入價格函式
    def clt_avg_amount(transactions):
        buy_transactions=[t for t in transactions if t["type"]=="buy"]
        if not buy_transactions:
            return 0
        total_amount=sum([t['amount'] for t in transactions])
        total_weight=sum([t['weight'] for t in transactions])
        return total_amount/total_weight if total_weight!=0 else 0
    #日期篩選
    start_str=request.form.get("start")
    end_str=request.form.get("end")
    query={"owner":session["nickname"]}
    if start_str and end_str:
        start_date=datetime.strptime(start_str,"%Y-%m-%dT%H:%M")
        end_date=datetime.strptime(end_str,"%Y-%m-%dT%H:%M")
        query["timestamp"]={"$gte": start_date, "$lte": end_date}
    records=list(gold_collection.find(query).sort("timestamp",-1))
    #統計資訊
    stats={
        "total_buy":sum(float(t["amount"]) for t in records if t["type"]=="buy"),
        "total_amount":sum(t["amount"] for t in records if t["type"]=="buy"),
        "total_avg_amount":clt_avg_amount(records),
        "total_weight":sum(t['weight'] for t in records if t["type"]=="buy")
    }   
    return render_template("home.html",records=records,stats=stats)

#新增
@app.route("/add",methods=["GET","POST"])
def add():
    if request.method=="POST":
        timestamp_str=request.form.get("timestamp")
        if timestamp_str:
            timestamp=datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M")
        else:
            timestamp=datetime.now()
        transaction={
            "type":request.form.get("type"),
            "weight":float(request.form.get("weight")),
            "price":float(request.form.get("price")),
            "amount":float(request.form.get("weight"))*float(request.form.get("price")),
            "note":request.form.get("note"),
            "timestamp":timestamp,
            "owner":session["nickname"]                                     
        }
        gold_collection.insert_one(transaction)
        return redirect("/homescreen")
    return render_template("add.html")

#刪除
@app.route("/delete/<id>",methods=["POST"])
def delete(id):
    gold_collection.delete_one({"_id":ObjectId(id),"owner":session["nickname"]})
    return redirect("/homescreen")

#修改
@app.route("/update/<id>",methods=["POST"])
def update(id):
    data=request.json
    try:
        gold_collection.update_one(
            {"_id":ObjectId(id)},
            {"$set": data} 
        )
        return jsonify({"success":True})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})
        



if __name__=="__main__":
    app.run(debug=True)





