import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { VRM, VRMUtils, VRMLoaderPlugin, VRMHumanBoneName } from '@pixiv/three-vrm'; //VRMSchema 不支持了
import { BVHLoader } from "three/examples/jsm/loaders/BVHLoader";
import { createVRMAnimationClip, VRMAnimationLoaderPlugin, VRMLookAtQuaternionProxy } from '@pixiv/three-vrm-animation';

// 播放  BVH 动作 BVH 先转换 vrma
// 网址 https://vrm-c.github.io/bvh2vrma/

(async () => {

    //定义变量
    let currentVrm = undefined;
    let currentMixer = undefined; //播放动画
    let blinkMixer = undefined; //眨眼动画
    const canvas = document.getElementById('canvas')
    //场景
    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
        35, canvas.clientWidth / canvas.clientHeight, 0.1, 1000)
    camera.position.set(0, 1.3, -1)
    //camera.rotation.set(0, Math.PI, 0)
    camera.lookAt(new THREE.Vector3(0.15, 1.25, 0));

    // 渲染器设置
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(canvas.clientWidth, canvas.clientHeight)
    // renderer.setClearColor(0x7fbfff, 1.0);
    renderer.setClearColor("0x000000", 0);
    document.body.appendChild(renderer.domElement);

    // 灯光
    const directionalLight = new THREE.DirectionalLight(0xff_ff_ff, Math.PI);
    directionalLight.position.set(1, 1, 1).normalize();
    scene.add(directionalLight);

    //GLTF 加载模型
    const loader = new GLTFLoader();
    loader.crossOrigin = 'anonymous';
    // 注意 此处要注册两个
    loader.register((parser) => {
        return new VRMLoaderPlugin(parser);
    });

    // 注意修改成带动画的vrm
    loader.register((parser) => {

        return new VRMAnimationLoaderPlugin(parser);

    });

    // load VRM
    const gltfVrm = await loader.loadAsync('vrm/1.vrm');
    const vrm = gltfVrm.userData.vrm;

    // calling these functions greatly improves the performance
    VRMUtils.removeUnnecessaryVertices(vrm.scene);
    VRMUtils.removeUnnecessaryJoints(vrm.scene);

    // Disable frustum culling
    vrm.scene.traverse((obj) => {

        obj.frustumCulled = false;

    });

    // 如果你想增加lookat  必须新增到动画中
    const lookAtQuatProxy = new VRMLookAtQuaternionProxy(vrm.lookAt);
    lookAtQuatProxy.name = 'lookAtQuaternionProxy';
    vrm.scene.add(lookAtQuatProxy);

    // Add VRM to the scene
    console.log(vrm);
    scene.add(vrm.scene);

    // load VRMA
    const gltfVrma = await loader.loadAsync('vrm/idle_loop.vrma');
    const vrmAnimation = gltfVrma.userData.vrmAnimations[0];

    // // create animation clip
    // const clip = createVRMAnimationClip(vrmAnimation, vrm);

    // //调整胳膊
    // // adjustAnimationClip(clip);


    // // play animation
    // const mixer = new THREE.AnimationMixer(vrm.scene);
    // const action = mixer.clipAction(clip);
    // action.setEffectiveTimeScale(2.0);
    // action.play();

    // 优化版本 增加眨眼动作
    // 定义剪辑1
    const clip = createVRMAnimationClip(vrmAnimation, vrm);
    // 创建眨眼动画
    const blinkTrack = new THREE.NumberKeyframeTrack(
        vrm.expressionManager.getExpressionTrackName('blink'),
        [0, 0.5, 1.0],//时间
        [0.0, 1.0, 0.0] //关键帧对应值
    );

    // 定义一个眨眼剪辑
    const blinkClip = new THREE.AnimationClip('BlinkAnimation', 1.0, [blinkTrack]);

    // 创建一个微微点头的动画
    const nodTrack = new THREE.QuaternionKeyframeTrack(
        vrm.humanoid.getNormalizedBoneNode('head').name + '.quaternion',
        [2.0, 2.5, 3.0, 3.5, 4.0], //时间可以与眨眼不在同一轨道上
        [
            0, 0, 0, 1,                 // 初始位置
            0.05, 0, 0, 0.9987, // 稍微低头
            0, 0, 0, 1,                 // 回到中间
            -0.025, 0, 0, 0.9997, // 稍微抬头
            0, 0, 0, 1                  // 回到初始位置
        ]
    );
    const nodClip = new THREE.AnimationClip('NodAnimation', 2.0, [nodTrack]);

    // 获取剪辑的轨道
    const originalTracks = clip.tracks;
    const blinkTracks = blinkClip.tracks;
    const nodTracks = nodClip.tracks;
    const mergedTracks = [...originalTracks, ...blinkTracks, ...nodTracks];
    // 创建一个合并剪辑
    const mergedClip = new THREE.AnimationClip('MergedAnimation', -1, mergedTracks);
    //创建一个动画混合器
    const mixer = new THREE.AnimationMixer(vrm.scene);
    const action = mixer.clipAction(mergedClip);
    action.setEffectiveTimeScale(1.0);
    action.setLoop(THREE.LoopRepeat);
    action.play();

    // helpers
    // const gridHelper = new THREE.GridHelper(10, 10);
    // scene.add(gridHelper);

    // const axesHelper = new THREE.AxesHelper(5);
    // scene.add(axesHelper);

    // animate
    const clock = new THREE.Clock();
    clock.start();

    function animate() {

        requestAnimationFrame(animate);

        const deltaTime = clock.getDelta();



        vrm.update(deltaTime);

        if (currentMixer != null) {
            console.log("渲染动画")
            currentMixer.update(deltaTime);
        } else {
            mixer.update(deltaTime);  //待机动画
            //眨眼动画 一下
            //prepareAnimation(vrm);

        }

        renderer.render(scene, camera);

    }

    animate();


    // 播放一个新动画
    async function playVRMAAnimation(vrm, vrmaUrl, timeScale = 2.0) {
        // 加载VRMA文件
        const gltfVrma = await loader.loadAsync(vrmaUrl);
        const vrmAnimation = gltfVrma.userData.vrmAnimations[0];

        // 创建动画剪辑
        const clip = createVRMAnimationClip(vrmAnimation, vrm);

        // 如果需要调整胳膊动画，取消下面这行的注释
        // adjustAnimationClip(clip);

        // 创建动画混合器并播放动画
        const mixer = new THREE.AnimationMixer(vrm.scene);
        const action = mixer.clipAction(clip);

        // 设置动画只播放一次
        action.setLoop(THREE.LoopOnce);
        action.clampWhenFinished = true;

        action.setEffectiveTimeScale(timeScale);

        // 监听动画完成事件
        mixer.addEventListener('finished', () => {
            console.log("播放结束")
            // 重新应用默认表情动画
            applyDefaultFaceExpression(vrm);
            //还原位置 及播放原来动画
            currentMixer = null

        });

        action.play();

        // 返回mixer，以便在外部更新动画
        currentMixer = mixer

        //return mixer;

    }

    // 默认的表情 经常在动画播放完毕时
    function applyDefaultFaceExpression(vrm) {

    }


    // 调整动画片段的辅助功能 暂时不使用
    function adjustAnimationClip(clip) {
        clip.tracks.forEach((track) => {
            console.log(track.name)
            if (track.name.includes('L_LowerArm') || track.name.includes('R_LowerArm')) {
                // Adjust rotation values for arm tracks
                for (let i = 0; i < track.values.length; i += 3) {
                    // Example: reduce rotation by 20%
                    track.values[i] *= 0.8;
                    track.values[i + 1] *= 0.8;
                    track.values[i + 2] *= 0.8;
                }
            }
        });
    }

    // 自定义动画
    function prepareAnimation(vrm) {

        blinkMixer = new THREE.AnimationMixer(vrm.scene);

        //眨眼 动画
        const blinkTrack = new THREE.NumberKeyframeTrack(
            vrm.expressionManager.getExpressionTrackName('blink'), // name
            [0.5, 0.5, 1.0], // times
            [0.0, 1.0, 0.0] // values
        );
        const clip = new THREE.AnimationClip('Animation', 1.0, [blinkTrack]); //可以新增其他自定义动画
        const action = blinkMixer.clipAction(clip);
        action.play();

    }
    //模拟说话
    function simulateSpeech(expressionManager, duration = 2000, interval = 100) {
        let time = 0;
        const intervalId = setInterval(() => {
            const value = Math.sin(time * 0.1) * 0.5 + 0.5;
            expressionManager.setValue('aa', value);
            expressionManager.setValue('ih', 1 - value);

            time += interval;
            if (time >= duration) {
                clearInterval(intervalId);
                expressionManager.setValue('aa', 0);
                expressionManager.setValue('ih', 0);
            }
        }, interval);
    }
    //  // 等待10秒后模拟说话
    //  setTimeout(() => {
    //     if (vrm && vrm.expressionManager) {
    //         simulateSpeech(vrm.expressionManager);
    //     } else {
    //         console.error('VRM or expressionManager not available');
    //     }
    // }, 10000);

    //开始说话
    async function simulateSpeechFromAudio(expressionManager, audioUrl) {
        // 创建音频上下文 web Audio  api
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();

        // 加载音频
        const response = await fetch(audioUrl);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        // 创建音频源和分析器
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;

        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;

        source.connect(analyser);
        analyser.connect(audioContext.destination);

        // 开始播放
        source.start();

        // 创建数据数组
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        // 动画循环
        let animationFrameId;
        function animate() {
            animationFrameId = requestAnimationFrame(animate);

            // 获取音频数据
            analyser.getByteFrequencyData(dataArray);

            // 计算平均音量
            const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;

            // console.log(average)
            // 将音量映射到0-1范围
            const volume = average / 255;
            // console.log(volume)
            // 设置表情值
            expressionManager.setValue('aa', volume * 10);
            expressionManager.setValue('ih', 1 - volume);

        }

        animate();

        // 音频播放结束后重置表情
        source.onended = () => {
            cancelAnimationFrame(animationFrameId);
            expressionManager.setValue('aa', 0);
            expressionManager.setValue('ih', 0);

        };
    }

    // 开始 sourceBuffer为播放器实例
    //一帧的表情
    let audioContext;
    let analyser;
    let source;
    async function simulateSpeechFromAudio2(expressionManager, mediaSource, audio) {
        // 开始音频分析和 VRM 模型控制
        // Create an AudioContext and analyser
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
        }
        if (!source) {
            // 将音频元件连接到分析仪
            source = audioContext.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioContext.destination);
        }
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        // 动画循环
        let animationFrameId;
        function animate() {
            animationFrameId = requestAnimationFrame(animate);

            // 获取音频数据
            analyser.getByteFrequencyData(dataArray);

            // 计算平均音量
            const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;

            //console.log(average)
            // 将音量映射到0-1范围
            const volume = average / 255;
            //console.log(volume)
            // 设置表情值
            expressionManager.setValue('aa', volume * 10);
            expressionManager.setValue('ih', 1 - volume);
        }

        animate();
    }

    window.ask = function ask(audioUrl) {
        if (vrm && vrm.expressionManager) {
            simulateSpeechFromAudio(vrm.expressionManager, audioUrl);
            //模拟一次动画 测试使用
            //playVRMAAnimation(vrm, 'vrm/VRMA_041.vrma')
        } else {
            console.error('VRM or expressionManager not available');
        }

    }

    // 新版语音-流式
    window.ask2 = function ask2(mediaSource, audio) {
        if (vrm && vrm.expressionManager) {
            simulateSpeechFromAudio2(vrm.expressionManager, mediaSource, audio);
        } else {
            console.error('VRM or expressionManager not available');
        }

    }

})();

