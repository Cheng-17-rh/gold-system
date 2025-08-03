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
                            
#註冊帳號
@app.route("/",methods=["GET","POST"])
def member():
    nickname=request.form.get("nickname")
    email=request.form.get("email")
    password=request.form.get("password")
    result=member_collection.find({
        "$or":[
            {"mickname":"nickname"},
               { "email":"email"}           
            ]  
    })
    if result !=None:
        return redirect("/error?msg=信箱已被使用")
    member_collection.insert_one({
        "nickname":"naickname",
        "email":"email",
        "password":"password"
    })
    return render_template("signupsuccess.html")

#錯誤
@app.route("/error")
def error():
    message=request.args.get("msg","出現未知的錯誤")
    return render_template("error.html",message=message)


#首頁
@app.route("/homescreen",methods=["GET","POST"])
def home():
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
    query={}
    if start_str and end_str:
        start_date=datetime.strptime(start_str,"%Y-%m-%dT%H:%M")
        end_date=datetime.strptime(end_str,"%Y-%m-%dT%H:%M")
        query["timestamp"]={"$gte": start_date, "$lte": end_date}
    records=list(gold_collection.find(query).sort("timestamp",-1))
    #統計資訊
    stats={
        "total_buy":sum(t["amount"] for t in records if t["type"]=="buy"),
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
            "timestamp":timestamp                                       
        }
        gold_collection.insert_one(transaction)
        return redirect("/")
    return render_template("add.html")

#刪除
@app.route("/delete/<id>",methods=["POST"])
def delete(id):
    gold_collection.delete_one({"_id":ObjectId(id)})
    return redirect("/homescreen")


if __name__=="__main__":
    app.run(debug=True)





