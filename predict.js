const {spawn} = require('child_process');

const child = spawn('python', ['./predict.py', 101]);

child.stdout.on('data', (result)=>{
  let str = result.toString();
  let lines = str.split(/\n/g);
  lines.pop(lines.length-1);
  // console.log(lines)

  let list1 = [];

  for(let i = 0; i < lines.length; i++){
    let data = lines[i].toString().replace(`b\'`, '').replace(`\'`,'');
    let buff = Buffer.from(data, 'base64');
    let text = buff.toString('utf-8');
    // console.log(text);
    list1.push(text);
  }
  // console.log(list1);
  for(let i = 0; i < list1.length; i++){
    console.log(list1[i]);
  }
})
