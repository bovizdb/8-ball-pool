import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const yAxis = new THREE.Vector3(0, 1, 0);
const zAxis = new THREE.Vector3(0, 0, 1);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 1000);
camera.position.set(0, 4, 0);
camera.rotation.x = -Math.PI/2;


const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio * 2);
document.body.appendChild(renderer.domElement);


const controls = new OrbitControls(camera, renderer.domElement);

controls.target.set(0, 1, 0);
controls.maxPolarAngle = 49*Math.PI/100;
controls.minAzimuthAngle = -49*Math.PI/100;
controls.maxDistance = 8;
controls.minDistance = 1;
// controls.autoRotate = true;
controls.autoRotateSpeed = 4;
controls.update();

const light1 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
const light2 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
const light3 = new THREE.SpotLight(0xFFFFFF, 10, 2.5, 60);
light1.position.set(-1.2, 2, 0);
light2.position.set(0, 2, 0)
light3.position.set(1.2, 2, 0);
scene.add(light1, light2, light3);

const loader = new GLTFLoader();

let table;

loader.load('/table.glb', function (glb) {
    
    table = glb.scene;
    table.position.set(0, 0, 0);
	scene.add(table);
    
}, undefined, function (error) {
    
    console.error(error);
    
});

let balls = {};

fetch('balls.json')
    .then(response => response.json())
    .then(data => {
        balls = data;
        Object.values(data).forEach(item => {
            loader.load(item.label+'.glb', function (glb) {
                let ball = glb.scene;
                let posx = 2*item.x/1000-1.88;
                let posz = 2*item.y/1000-0.91;
                ball.position.set(posx, 1.00, posz);
                ball.scale.set(0.0525, 0.0525, 0.0525);
                let rotx = Math.random()*Math.PI*2;
                let roty = Math.random()*Math.PI*2;
                let rotz = Math.random()*Math.PI*2;
                ball.rotation.set(rotx, roty, rotz);
                scene.add(ball);
                
            }, undefined, function (error) {
                console.error(error);
            });
        });
        console.log(balls);
    })
    .catch(err => console.error("Fetch error:", err));

console.log(balls);

let cueRotation = 0;

fetch('cue.txt')
    .then(response => response.text())
    .then(data => {
        cueRotation = parseFloat(data);
    })
    .catch(err => console.error("Fetch error:", err));

// for (let i = 0; i < 16; i++) {
//     loader.load('/'+i+'.glb', function (glb) {
//         let ball = glb.scene;
//         let posx = Math.random()*3.6 - 1.8;
//         let posz = Math.random()*1.6 - 0.8;
//         ball.position.set(posx, 1.00, posz);
//         ball.scale.set(0.0525, 0.0525, 0.0525);
//         let rotx = Math.random()*Math.PI*2;
//         let roty = Math.random()*Math.PI*2;
//         let rotz = Math.random()*Math.PI*2;
//         ball.rotation.set(rotx, roty, rotz);
//         scene.add(ball);
//         balls.push(ball);

//     }, undefined, function (error) {
//         console.error(error);
//     });

// }

loader.load('cue.glb', function (glb) {
    let cue = glb.scene;
    let posx = 2*balls[0].x/1000-1.88;
    let posz = 2*balls[0].y/1000-0.91;
    cue.position.set(posx, 1, posz);
    cue.rotation.set(1.7, 0, 0);
    cue.rotateOnWorldAxis(yAxis, Math.PI-cueRotation);
    // scene.add(cue);

}, undefined, function (error) {
    
    console.error(error);
    
});

function drawLine(start, end) {
    const material = new THREE.MeshBasicMaterial({color: 0xFFFFFF});
    const points = [];
    points.push(start);
    points.push(end);
    const geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), 64, 0.004, 8, false);
    const line = new THREE.Mesh(geometry, material);
    scene.add(line);
}

let b = 0;

function animate() {
    //requestAnimationFrame(animate);
    
    if (balls.length == 16 && b == 0) {
        b = 1;
        //drawLine(balls[0].position, balls[Math.round(Math.random()*14+1)].position);
    }
    // camera.rotateOnWorldAxis(yAxis, 0.001);
	renderer.render(scene, camera);
    controls.update();
    for (let i = 0; i < balls.length; i++) {
        //balls[i].rotation.y += 0.02;
    }
}
renderer.setAnimationLoop(animate);
//animate();