let pass1 = document.querySelector("#password")
let pass2 = document.querySelector("#c_password")
let sign_up = document.querySelector("#signup")
let error = document.querySelector("#errorMsg")

sign_up.addEventListener("submit", (event) => {
    if(pass1.value !== pass2.value){
        event.preventDefault(); 
        error.innerHTML = "<p>Password doesn't match</p>"
    }else{
        error.innerText = "";
    }
})
