function enableEdit(id){
    const row=document.getElementById("row-"+id)
    const cells=row.querySelectorAll("td")
    
    //保留原本的資料
    for (let i=0 ; i<cells.length-1; i++) {
        const text=cells[i].innerText
        cells[i].setAttribute("data-orignal",text)
        cells[i].innerHTML=`<input type=text value="${text}"/>`;
    }
    
    //改編操作欄位 修改->確認or取消
    const actionCell=cell[cell.length-1];
    actionCell.innerHTML=`
        <button onclick="confirmEdit('$(id)')">確認</button>;
        <button onclick="cancelEdit('$(id)')">取消</button>;
    `;
}


//確認修改
function confirmEdit(){
    const row=document.getElementById("row"+id);
    const inputs=row.querySelectorAll("td input");
    let updateData=[];

    //取出輸入的值
    inputs.forEach(input => {
        updateData.push(input.value);
    });

    //資料欄位
    const payload={
        type:updateData[0],
        weight:updateData[1],
        price:updateData[2],
        amount:updateData[3],
        note:updateData[4],
        timestamp:updateData[5]
    };

    //呼叫後端API更新
    fetch(`/update/${id}`, {
        method:"POST",
        headers: {
            "Content-Type":"application/json"
        },
        body:JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const cells=row.querySelectorAll("td")
            cells[0].innerText=payload.type;
            cells[1].innerText=payload.weight;
            cells[2].innerText=payload.price;
            cells[3].innerText=payload.amount;
            cells[4].innerText=payload.note;
            cells[5].innerText=payload.timestamp;
            cells[6].innerHTML=`
                    <form action="{{url_for('delete',id=t._id|string) }}" method="POST" style="display:inline;">
                        <button type="submit">刪除</button>
                    </form>
                    <button onclick="enableEdit('{{t._id}}')">修改</button>
                    `;         
        } else {
            alert("更新失敗");
        }
    });
}

//取消修改
function cancelEdit(id) {
    const row=document.getElementById("row"+id);
    const cells=row.querySelectorAll("td");

    //還原元交易資料
    for (let i=0;i<cells.length-1;i++) {
        const orignal=cells[i].getAttribute("data-orginal")
        cells[i].innerText=orignal;
    }

    //還原操作按鈕 正確取消->修改刪除
    cells[cells.length-1].innerHTML=`
        <form action="{{url_for('delete',id=t._id|string) }}" method="POST" style="display:inline;">
            <button type="submit">刪除</button>
        </form>
        <button onclick="enableEdit('{{t._id}}')">修改</button>
        `; 
}


