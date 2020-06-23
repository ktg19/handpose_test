<template>
  <v-layout
    column
    justify-center
    align-center
  >
    <v-flex
      xs12
      sm8
      md6
    >
        <video id="camera" width="600" height="400"></video>
    </v-flex>
  </v-layout>
</template>

<script>
const handpose = require('@tensorflow-models/handpose');
const axios = require('axios')
export default {
  data: function() {
    return{
      model: null
    }
  },
  components: {
  },
  mounted: async function(){
      const video = document.querySelector("#camera");

      /** カメラ設定 */
      const constraints = {
        audio: false,
        video: {
          width: 600,
          height: 400,
          facingMode: "user"   // フロントカメラ
        }
      };

      navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
          video.srcObject = stream;
          video.onloadedmetadata = (e) => {
            video.play();
          };
        })
        .catch((err) => {
          console.log(err.name + ": " + err.message);
        });

      this.model = await handpose.load(); //モデル読み込み

      setInterval(async function(){this.estimate(this.model)}.bind(this), 100)

      // setInterval(async function(model){
      //   const predictions = await this.model.estimateHands(document.querySelector("#camera"));//#cameraの内容から予測
      //   if (predictions.length > 0) {
      //     axios('/api/save', {params: {predictions: predictions}});
      //   }
      // }.bind(this),100)
    
  },
  methods:{
    estimate: async function(){
      const predictions = await this.model.estimateHands(document.querySelector("#camera"));//#cameraの内容から予測
      if (predictions.length > 0) {
        axios('/api/save', {params: {predictions: predictions}});
      }
    }
  }
}
</script>
