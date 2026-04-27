let ws;
let me;
let target = null;

function connect(){
    ws = new WebSocket(
        (location.protocol==="https:"?"wss://":"ws://")
        + location.host + "/ws"
    );

    ws.onmessage = e=>{
        let d = JSON.parse(e.data);

        if(d.type==="login_ok"){
            document.getElementById("login").style.display="none";
            document.getElementById("app").style.display="flex";
        }

        if(d.type==="users"){
            let ul=document.getElementById("users");
            ul.innerHTML="";

            d.data.forEach(u=>{
                if(u===me) return;

                let li=document.createElement("li");
                li.innerText=u;

                li.onclick=()=>{
                    target=u;
                    document.getElementById("title").innerText="Chat with "+u;
                };

                ul.appendChild(li);
            });
        }

        if(d.type==="msg" || d.type==="room"){
            addMsg(d.from,d.msg,false,d.time);
        }
    };
}

function login(){
    me=document.getElementById("name").value;
    connect();

    ws.onopen=()=>{
        ws.send(JSON.stringify({
            type:"login",
            name:me,
            password:document.getElementById("pass").value
        }));
    };
}

function register(){
    connect();

    ws.onopen=()=>{
        ws.send(JSON.stringify({
            type:"register",
            name:document.getElementById("name").value,
            password:document.getElementById("pass").value
        }));
    };
}

function send(){
    let m=document.getElementById("msg").value;
    if(!m) return;

    if(target){
        ws.send(JSON.stringify({type:"dm",to:target,msg:m}));
    }else{
        ws.send(JSON.stringify({type:"room",room:"global",msg:m}));
    }

    addMsg("Me",m,true,new Date().toLocaleTimeString());
    document.getElementById("msg").value="";
}

function addMsg(f,m,isMe,t){
    let div=document.createElement("div");
    div.className="bubble "+(isMe?"me":"other");

    div.innerHTML = `<div>${m}</div><span>${t}</span>`;

    document.getElementById("chat").appendChild(div);
            }
