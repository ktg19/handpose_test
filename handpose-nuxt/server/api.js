const express = require('express')
const router = express.Router()
const fs = require('fs')

const dateString = () => {
  let dt    = new Date();// 現在時刻の取得 dt.getFullYear(), 
  const dateArray = [dt.getMonth()+1, dt.getDate(), dt.getHours(), dt.getMinutes(), dt.getSeconds(), dt.getMilliseconds()]
  for(let i = 0;i<dateArray.length;i++){
    const withZero = '000' + dateArray[i]
    const digits = (i != dateArray.length - 1 ? 2 : 4) //ミリ秒は4桁
    dateArray[i] = withZero.substr(withZero.length-digits, digits)
  }
  return dateArray.join('')
}

router.get('/save', (req, res, next) => {
  console.log("api/saveに入りました")
  console.log(req.query.predictions)
  const now = dateString()
  const data = {
    hoge: 100,
    foo: 'a',
    bar: true,
  };
  const filename = 'json_files\\predictions' + now + '.json'

  fs.writeFile(filename, JSON.stringify(req.query.predictions[0], null, '    '), function (err) {
    // .replace(/\\/g, '').replace(/\"/g, '')  
    if (err) { throw err; }
      console.log('jsonが作成されました');
  })//JSON.stringify(req.query.predictions, null, '    ')
  
  const param = { test: 'success' }
  res.header('Content-Type', 'application/json; charset=utf-8')
  res.send(param)
})

module.exports = router