//efect giao dien
$(document).ready(function(){
  $("#left .custom-sentence ").hide();
  $("#tuychinhtheocau").click(function(){
    $("#left .custom-sentence ").show();
  });
  $("#tudongtomtat").click(function(){
    $("#left .custom-sentence ").hide();
  });
  // $("#topic ").hide();
  // $("#tudongtomtat").click(function(){
  //   $("#topic").show();
  // });
});
//function functionResultMid
function functionResultTop(){
    var textResum = document.getElementById("textright_top").value;
    document.getElementById("textright").value = textResum;
    countRight();
}
function functionResultMid(){
    var textResum = document.getElementById("textright_mid").value;
    document.getElementById("textright").value = textResum;
    countRight();
}
function functionResultButtom(){
    var textResum = document.getElementById("textright_buttom").value;
    document.getElementById("textright").value = textResum;
    countRight();
}
// chuc nang tu day
//nút copy
function functionCopy() {
  var copyText = document.getElementById("textright");
  copyText.select();
  document.execCommand("copy");
}
//nút xóa văn bản
function functionDelete(){
  var deleteTextLeft = document.getElementById("textleft");
  deleteTextLeft.value ='';
  var deleteTextRight = document.getElementById("textright");
  deleteTextRight.value ='';
  var deleteTextRight = document.getElementById("textright_mid");
  deleteTextRight.value ='';
  var deleteTextRight = document.getElementById("textright_buttom");
  deleteTextRight.value ='';
  document.getElementById("topic").innerHTML = "";
  document.getElementById("count_left").innerText = "0/20000";
  document.getElementById("count_right").innerText = "0";
}
//nút export click
function exportHTML(){
  var textoutput =document.getElementById("textright").value;
  if(textoutput == "")
    alert("File tải xuống trống!")
  else{
    var header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' "+
    "xmlns:w='urn:schemas-microsoft-com:office:word' "+
    "xmlns='http://www.w3.org/TR/REC-html40'>"+
    "<head><meta charset='utf-8'><title>Export HTML to Word Document with JavaScript</title></head><body>";
    var footer = "</body></html>";
    var sourceHTML = header+textoutput+footer;
    var source = 'data:application/vnd.ms-word;charset=utf-8,' + encodeURIComponent(sourceHTML);
    var fileDownload = document.createElement("a");
    document.body.appendChild(fileDownload);
    fileDownload.href = source;
    fileDownload.download = 'document.doc';
    fileDownload.click();
    document.body.removeChild(fileDownload);  
  }
}
//openfile
function openFile(event) {

      var input = event.target;
      var reader = new FileReader();
      reader.onload = function() {
        var zip = new JSZip(reader.result);
        var doc = new window.docxtemplater().loadZip(zip);
        var text = doc.getFullText();
        var node = document.getElementById('textleft');
        node.value = text;
        countLeft();
      };
      reader.readAsBinaryString(input.files[0]);
};
//function get đuôi file 
function getExtension(file1) {
      var extension = file1.split('.').pop();
      return  extension;
};
function functionImport(){
  var a = document.querySelector('#myFile');
  var fileName = a.value; 
  var extension = getExtension(fileName);

  switch(extension) {
    case "docx":
        openFile(event); 
        break;
    default:
        alert("Không hỗ trợ file này!");
  }
}
//rang buoc input
function functionSummaration(){
  var textinput =document.getElementById("textleft").value;
  var countWords = textinput.length;
  if (countWords == 20000) {
    alert("Bạn chỉ được phép tóm tắt văn bản dưới 10000 kí tự!");
  }
  if (countWords == 0) {
    alert("Văn bản trống, mời bạn nhập lại!");
    return false
  }
  countRight();
  countLeft(); 
}
//rang buoc chi cho nhap so cau
function checkInput(ob) {
  var invalidChars = /[^0-9]/gi
  if(invalidChars.test(ob.value)) {
          ob.value = ob.value.replace(invalidChars,"");
      }
}
//count wwords
document.getElementById("textleft").addEventListener('keyup', count);
function count(){
  var resultArray = [];
  var str = this.value.replace(/[\t\n\r\.\?\!\@\#\$\%\^\&\*\(\)\-\_\+\`\~\=\{\}\[\]\:\;\"\'\,\<\>\.\?]/gm,' ');
  var wordArray = str.split(" ");
  for (var i = 0; i < wordArray.length; i++) {
    var item = wordArray[i].trim();
    if(item.length > 0){
      resultArray.push(item);
    }
  }
  document.getElementById("count_left").innerText = resultArray.length +"/20000";
}
function countRight(){
  var resultArray = [];
  var str = document.getElementById("textright").value.replace(/[\t\n\r\.\?\!\@\#\$\%\^\&\*\(\)\-\_\+\`\~\=\{\}\[\]\:\;\"\'\,\<\>\.\?]/gm,' ');
  var wordArray = str.split(" ");
  for (var i = 0; i < wordArray.length; i++) {
    var item = wordArray[i].trim();
    if(item.length > 0){
      resultArray.push(item);
    }
  }
  document.getElementById("count_right").innerText = resultArray.length ;
}
function countLeft(){
  var resultArray = [];
  var str = document.getElementById("textleft").value.replace(/[\t\n\r\.\?\!\@\#\$\%\^\&\*\(\)\-\_\+\`\~\=\{\}\[\]\:\;\"\'\,\<\>\.\?]/gm,' ');
  var wordArray = str.split(" ");
  for (var i = 0; i < wordArray.length; i++) {
    var item = wordArray[i].trim();
    if(item.length > 0){
      resultArray.push(item);
    }
  }
  document.getElementById("count_left").innerText = resultArray.length +"/20000";
}
