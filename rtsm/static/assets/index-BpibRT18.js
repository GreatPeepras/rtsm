(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const r of document.querySelectorAll('link[rel="modulepreload"]'))n(r);new MutationObserver(r=>{for(const s of r)if(s.type==="childList")for(const o of s.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&n(o)}).observe(document,{childList:!0,subtree:!0});function t(r){const s={};return r.integrity&&(s.integrity=r.integrity),r.referrerPolicy&&(s.referrerPolicy=r.referrerPolicy),r.crossOrigin==="use-credentials"?s.credentials="include":r.crossOrigin==="anonymous"?s.credentials="omit":s.credentials="same-origin",s}function n(r){if(r.ep)return;r.ep=!0;const s=t(r);fetch(r.href,s)}})();/**
 * @license
 * Copyright 2010-2023 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const _u="160",ls={ROTATE:0,DOLLY:1,PAN:2},cs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},jm=0,vf=1,$m=2,Zd=1,Km=2,Ii=3,gr=0,Ln=1,xi=2,ar=0,Fs=1,xf=2,Mf=3,Sf=4,Zm=5,Fr=100,Jm=101,Qm=102,yf=103,Ef=104,eg=200,tg=201,ng=202,ig=203,Yc=204,jc=205,rg=206,sg=207,og=208,ag=209,lg=210,cg=211,ug=212,fg=213,hg=214,dg=0,pg=1,mg=2,qa=3,gg=4,_g=5,vg=6,xg=7,Jd=0,Mg=1,Sg=2,lr=0,yg=1,Eg=2,Tg=3,bg=4,Ag=5,wg=6,Qd=300,ks=301,Hs=302,$c=303,Kc=304,al=306,Zc=1e3,ui=1001,Jc=1002,Sn=1003,Tf=1004,Fl=1005,Kn=1006,Rg=1007,No=1008,cr=1009,Cg=1010,Lg=1011,vu=1012,ep=1013,sr=1014,or=1015,Fo=1016,tp=1017,np=1018,kr=1020,Pg=1021,fi=1023,Dg=1024,Ug=1025,Hr=1026,Gs=1027,Ig=1028,ip=1029,Ng=1030,rp=1031,sp=1033,Ol=33776,Bl=33777,zl=33778,kl=33779,bf=35840,Af=35841,wf=35842,Rf=35843,op=36196,Cf=37492,Lf=37496,Pf=37808,Df=37809,Uf=37810,If=37811,Nf=37812,Ff=37813,Of=37814,Bf=37815,zf=37816,kf=37817,Hf=37818,Gf=37819,Vf=37820,Wf=37821,Hl=36492,Xf=36494,qf=36495,Fg=36283,Yf=36284,jf=36285,$f=36286,ap=3e3,Gr=3001,Og=3200,Bg=3201,zg=0,kg=1,Qn="",fn="srgb",Wi="srgb-linear",xu="display-p3",ll="display-p3-linear",Ya="linear",It="srgb",ja="rec709",$a="p3",us=7680,Kf=519,Hg=512,Gg=513,Vg=514,lp=515,Wg=516,Xg=517,qg=518,Yg=519,Qc=35044,Zf="300 es",eu=1035,zi=2e3,Ka=2001;class jr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const r=this._listeners[e];if(r!==void 0){const s=r.indexOf(t);s!==-1&&r.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const r=n.slice(0);for(let s=0,o=r.length;s<o;s++)r[s].call(this,e);e.target=null}}}const dn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],Ga=Math.PI/180,tu=180/Math.PI;function ur(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(dn[i&255]+dn[i>>8&255]+dn[i>>16&255]+dn[i>>24&255]+"-"+dn[e&255]+dn[e>>8&255]+"-"+dn[e>>16&15|64]+dn[e>>24&255]+"-"+dn[t&63|128]+dn[t>>8&255]+"-"+dn[t>>16&255]+dn[t>>24&255]+dn[n&255]+dn[n>>8&255]+dn[n>>16&255]+dn[n>>24&255]).toLowerCase()}function En(i,e,t){return Math.max(e,Math.min(t,i))}function jg(i,e){return(i%e+e)%e}function Gl(i,e,t){return(1-t)*i+t*e}function Jf(i){return(i&i-1)===0&&i!==0}function nu(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Oi(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function At(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const $g={DEG2RAD:Ga};class qe{constructor(e=0,t=0){qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6],this.y=r[1]*t+r[4]*n+r[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(En(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),r=Math.sin(t),s=this.x-e.x,o=this.y-e.y;return this.x=s*n-o*r+e.x,this.y=s*r+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class at{constructor(e,t,n,r,s,o,a,l,c){at.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,o,a,l,c)}set(e,t,n,r,s,o,a,l,c){const u=this.elements;return u[0]=e,u[1]=r,u[2]=a,u[3]=t,u[4]=s,u[5]=l,u[6]=n,u[7]=o,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,o=n[0],a=n[3],l=n[6],c=n[1],u=n[4],f=n[7],d=n[2],m=n[5],v=n[8],M=r[0],p=r[3],h=r[6],x=r[1],_=r[4],y=r[7],D=r[2],b=r[5],R=r[8];return s[0]=o*M+a*x+l*D,s[3]=o*p+a*_+l*b,s[6]=o*h+a*y+l*R,s[1]=c*M+u*x+f*D,s[4]=c*p+u*_+f*b,s[7]=c*h+u*y+f*R,s[2]=d*M+m*x+v*D,s[5]=d*p+m*_+v*b,s[8]=d*h+m*y+v*R,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8];return t*o*u-t*a*c-n*s*u+n*a*l+r*s*c-r*o*l}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],f=u*o-a*c,d=a*l-u*s,m=c*s-o*l,v=t*f+n*d+r*m;if(v===0)return this.set(0,0,0,0,0,0,0,0,0);const M=1/v;return e[0]=f*M,e[1]=(r*c-u*n)*M,e[2]=(a*n-r*o)*M,e[3]=d*M,e[4]=(u*t-r*l)*M,e[5]=(r*s-a*t)*M,e[6]=m*M,e[7]=(n*l-c*t)*M,e[8]=(o*t-n*s)*M,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,r,s,o,a){const l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*o+c*a)+o+e,-r*c,r*l,-r*(-c*o+l*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(Vl.makeScale(e,t)),this}rotate(e){return this.premultiply(Vl.makeRotation(-e)),this}translate(e,t){return this.premultiply(Vl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<9;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Vl=new at;function cp(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Za(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Kg(){const i=Za("canvas");return i.style.display="block",i}const Qf={};function Lo(i){i in Qf||(Qf[i]=!0,console.warn(i))}const eh=new at().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),th=new at().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),ia={[Wi]:{transfer:Ya,primaries:ja,toReference:i=>i,fromReference:i=>i},[fn]:{transfer:It,primaries:ja,toReference:i=>i.convertSRGBToLinear(),fromReference:i=>i.convertLinearToSRGB()},[ll]:{transfer:Ya,primaries:$a,toReference:i=>i.applyMatrix3(th),fromReference:i=>i.applyMatrix3(eh)},[xu]:{transfer:It,primaries:$a,toReference:i=>i.convertSRGBToLinear().applyMatrix3(th),fromReference:i=>i.applyMatrix3(eh).convertLinearToSRGB()}},Zg=new Set([Wi,ll]),Tt={enabled:!0,_workingColorSpace:Wi,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(i){if(!Zg.has(i))throw new Error(`Unsupported working color space, "${i}".`);this._workingColorSpace=i},convert:function(i,e,t){if(this.enabled===!1||e===t||!e||!t)return i;const n=ia[e].toReference,r=ia[t].fromReference;return r(n(i))},fromWorkingColorSpace:function(i,e){return this.convert(i,this._workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this._workingColorSpace)},getPrimaries:function(i){return ia[i].primaries},getTransfer:function(i){return i===Qn?Ya:ia[i].transfer}};function Os(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Wl(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}let fs;class up{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{fs===void 0&&(fs=Za("canvas")),fs.width=e.width,fs.height=e.height;const n=fs.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=fs}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Za("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const r=n.getImageData(0,0,e.width,e.height),s=r.data;for(let o=0;o<s.length;o++)s[o]=Os(s[o]/255)*255;return n.putImageData(r,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Os(t[n]/255)*255):t[n]=Os(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let Jg=0;class fp{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Jg++}),this.uuid=ur(),this.data=e,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},r=this.data;if(r!==null){let s;if(Array.isArray(r)){s=[];for(let o=0,a=r.length;o<a;o++)r[o].isDataTexture?s.push(Xl(r[o].image)):s.push(Xl(r[o]))}else s=Xl(r);n.url=s}return t||(e.images[this.uuid]=n),n}}function Xl(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?up.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Qg=0;class Pn extends jr{constructor(e=Pn.DEFAULT_IMAGE,t=Pn.DEFAULT_MAPPING,n=ui,r=ui,s=Kn,o=No,a=fi,l=cr,c=Pn.DEFAULT_ANISOTROPY,u=Qn){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Qg++}),this.uuid=ur(),this.name="",this.source=new fp(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=r,this.magFilter=s,this.minFilter=o,this.anisotropy=c,this.format=a,this.internalFormat=null,this.type=l,this.offset=new qe(0,0),this.repeat=new qe(1,1),this.center=new qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new at,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,typeof u=="string"?this.colorSpace=u:(Lo("THREE.Texture: Property .encoding has been replaced by .colorSpace."),this.colorSpace=u===Gr?fn:Qn),this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.needsPMREMUpdate=!1}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Qd)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Zc:e.x=e.x-Math.floor(e.x);break;case ui:e.x=e.x<0?0:1;break;case Jc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Zc:e.y=e.y-Math.floor(e.y);break;case ui:e.y=e.y<0?0:1;break;case Jc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}get encoding(){return Lo("THREE.Texture: Property .encoding has been replaced by .colorSpace."),this.colorSpace===fn?Gr:ap}set encoding(e){Lo("THREE.Texture: Property .encoding has been replaced by .colorSpace."),this.colorSpace=e===Gr?fn:Qn}}Pn.DEFAULT_IMAGE=null;Pn.DEFAULT_MAPPING=Qd;Pn.DEFAULT_ANISOTROPY=1;class an{constructor(e=0,t=0,n=0,r=1){an.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=r}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,r){return this.x=e,this.y=t,this.z=n,this.w=r,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*r+o[12]*s,this.y=o[1]*t+o[5]*n+o[9]*r+o[13]*s,this.z=o[2]*t+o[6]*n+o[10]*r+o[14]*s,this.w=o[3]*t+o[7]*n+o[11]*r+o[15]*s,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,r,s;const l=e.elements,c=l[0],u=l[4],f=l[8],d=l[1],m=l[5],v=l[9],M=l[2],p=l[6],h=l[10];if(Math.abs(u-d)<.01&&Math.abs(f-M)<.01&&Math.abs(v-p)<.01){if(Math.abs(u+d)<.1&&Math.abs(f+M)<.1&&Math.abs(v+p)<.1&&Math.abs(c+m+h-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const _=(c+1)/2,y=(m+1)/2,D=(h+1)/2,b=(u+d)/4,R=(f+M)/4,q=(v+p)/4;return _>y&&_>D?_<.01?(n=0,r=.707106781,s=.707106781):(n=Math.sqrt(_),r=b/n,s=R/n):y>D?y<.01?(n=.707106781,r=0,s=.707106781):(r=Math.sqrt(y),n=b/r,s=q/r):D<.01?(n=.707106781,r=.707106781,s=0):(s=Math.sqrt(D),n=R/s,r=q/s),this.set(n,r,s,t),this}let x=Math.sqrt((p-v)*(p-v)+(f-M)*(f-M)+(d-u)*(d-u));return Math.abs(x)<.001&&(x=1),this.x=(p-v)/x,this.y=(f-M)/x,this.z=(d-u)/x,this.w=Math.acos((c+m+h-1)/2),this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class e_ extends jr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new an(0,0,e,t),this.scissorTest=!1,this.viewport=new an(0,0,e,t);const r={width:e,height:t,depth:1};n.encoding!==void 0&&(Lo("THREE.WebGLRenderTarget: option.encoding has been replaced by option.colorSpace."),n.colorSpace=n.encoding===Gr?fn:Qn),n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Kn,depthBuffer:!0,stencilBuffer:!1,depthTexture:null,samples:0},n),this.texture=new Pn(r,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.flipY=!1,this.texture.generateMipmaps=n.generateMipmaps,this.texture.internalFormat=n.internalFormat,this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}setSize(e,t,n=1){(this.width!==e||this.height!==t||this.depth!==n)&&(this.width=e,this.height=t,this.depth=n,this.texture.image.width=e,this.texture.image.height=t,this.texture.image.depth=n,this.dispose()),this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.texture=e.texture.clone(),this.texture.isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new fp(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Xr extends e_{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class hp extends Pn{constructor(e=null,t=1,n=1,r=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Sn,this.minFilter=Sn,this.wrapR=ui,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class t_ extends Pn{constructor(e=null,t=1,n=1,r=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:r},this.magFilter=Sn,this.minFilter=Sn,this.wrapR=ui,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class _r{constructor(e=0,t=0,n=0,r=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=r}static slerpFlat(e,t,n,r,s,o,a){let l=n[r+0],c=n[r+1],u=n[r+2],f=n[r+3];const d=s[o+0],m=s[o+1],v=s[o+2],M=s[o+3];if(a===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=f;return}if(a===1){e[t+0]=d,e[t+1]=m,e[t+2]=v,e[t+3]=M;return}if(f!==M||l!==d||c!==m||u!==v){let p=1-a;const h=l*d+c*m+u*v+f*M,x=h>=0?1:-1,_=1-h*h;if(_>Number.EPSILON){const D=Math.sqrt(_),b=Math.atan2(D,h*x);p=Math.sin(p*b)/D,a=Math.sin(a*b)/D}const y=a*x;if(l=l*p+d*y,c=c*p+m*y,u=u*p+v*y,f=f*p+M*y,p===1-a){const D=1/Math.sqrt(l*l+c*c+u*u+f*f);l*=D,c*=D,u*=D,f*=D}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=f}static multiplyQuaternionsFlat(e,t,n,r,s,o){const a=n[r],l=n[r+1],c=n[r+2],u=n[r+3],f=s[o],d=s[o+1],m=s[o+2],v=s[o+3];return e[t]=a*v+u*f+l*m-c*d,e[t+1]=l*v+u*d+c*f-a*m,e[t+2]=c*v+u*m+a*d-l*f,e[t+3]=u*v-a*f-l*d-c*m,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,r){return this._x=e,this._y=t,this._z=n,this._w=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,r=e._y,s=e._z,o=e._order,a=Math.cos,l=Math.sin,c=a(n/2),u=a(r/2),f=a(s/2),d=l(n/2),m=l(r/2),v=l(s/2);switch(o){case"XYZ":this._x=d*u*f+c*m*v,this._y=c*m*f-d*u*v,this._z=c*u*v+d*m*f,this._w=c*u*f-d*m*v;break;case"YXZ":this._x=d*u*f+c*m*v,this._y=c*m*f-d*u*v,this._z=c*u*v-d*m*f,this._w=c*u*f+d*m*v;break;case"ZXY":this._x=d*u*f-c*m*v,this._y=c*m*f+d*u*v,this._z=c*u*v+d*m*f,this._w=c*u*f-d*m*v;break;case"ZYX":this._x=d*u*f-c*m*v,this._y=c*m*f+d*u*v,this._z=c*u*v-d*m*f,this._w=c*u*f+d*m*v;break;case"YZX":this._x=d*u*f+c*m*v,this._y=c*m*f+d*u*v,this._z=c*u*v-d*m*f,this._w=c*u*f-d*m*v;break;case"XZY":this._x=d*u*f-c*m*v,this._y=c*m*f-d*u*v,this._z=c*u*v+d*m*f,this._w=c*u*f+d*m*v;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,r=Math.sin(n);return this._x=e.x*r,this._y=e.y*r,this._z=e.z*r,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],r=t[4],s=t[8],o=t[1],a=t[5],l=t[9],c=t[2],u=t[6],f=t[10],d=n+a+f;if(d>0){const m=.5/Math.sqrt(d+1);this._w=.25/m,this._x=(u-l)*m,this._y=(s-c)*m,this._z=(o-r)*m}else if(n>a&&n>f){const m=2*Math.sqrt(1+n-a-f);this._w=(u-l)/m,this._x=.25*m,this._y=(r+o)/m,this._z=(s+c)/m}else if(a>f){const m=2*Math.sqrt(1+a-n-f);this._w=(s-c)/m,this._x=(r+o)/m,this._y=.25*m,this._z=(l+u)/m}else{const m=2*Math.sqrt(1+f-n-a);this._w=(o-r)/m,this._x=(s+c)/m,this._y=(l+u)/m,this._z=.25*m}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(En(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const r=Math.min(1,t/n);return this.slerp(e,r),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,r=e._y,s=e._z,o=e._w,a=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+o*a+r*c-s*l,this._y=r*u+o*l+s*a-n*c,this._z=s*u+o*c+n*l-r*a,this._w=o*u-n*a-r*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,r=this._y,s=this._z,o=this._w;let a=o*e._w+n*e._x+r*e._y+s*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=r,this._z=s,this;const l=1-a*a;if(l<=Number.EPSILON){const m=1-t;return this._w=m*o+t*this._w,this._x=m*n+t*this._x,this._y=m*r+t*this._y,this._z=m*s+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,a),f=Math.sin((1-t)*u)/c,d=Math.sin(t*u)/c;return this._w=o*f+this._w*d,this._x=n*f+this._x*d,this._y=r*f+this._y*d,this._z=s*f+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=Math.random(),t=Math.sqrt(1-e),n=Math.sqrt(e),r=2*Math.PI*Math.random(),s=2*Math.PI*Math.random();return this.set(t*Math.cos(r),n*Math.sin(s),n*Math.cos(s),t*Math.sin(r))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class k{constructor(e=0,t=0,n=0){k.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(nh.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(nh.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*r,this.y=s[1]*t+s[4]*n+s[7]*r,this.z=s[2]*t+s[5]*n+s[8]*r,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,r=this.z,s=e.elements,o=1/(s[3]*t+s[7]*n+s[11]*r+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*r+s[12])*o,this.y=(s[1]*t+s[5]*n+s[9]*r+s[13])*o,this.z=(s[2]*t+s[6]*n+s[10]*r+s[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,r=this.z,s=e.x,o=e.y,a=e.z,l=e.w,c=2*(o*r-a*n),u=2*(a*t-s*r),f=2*(s*n-o*t);return this.x=t+l*c+o*f-a*u,this.y=n+l*u+a*c-s*f,this.z=r+l*f+s*u-o*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,r=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*r,this.y=s[1]*t+s[5]*n+s[9]*r,this.z=s[2]*t+s[6]*n+s[10]*r,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,r=e.y,s=e.z,o=t.x,a=t.y,l=t.z;return this.x=r*l-s*a,this.y=s*o-n*l,this.z=n*a-r*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return ql.copy(this).projectOnVector(e),this.sub(ql)}reflect(e){return this.sub(ql.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(En(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,r=this.z-e.z;return t*t+n*n+r*r}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const r=Math.sin(t)*e;return this.x=r*Math.sin(n),this.y=Math.cos(t)*e,this.z=r*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),r=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=r,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=(Math.random()-.5)*2,t=Math.random()*Math.PI*2,n=Math.sqrt(1-e**2);return this.x=n*Math.cos(t),this.y=n*Math.sin(t),this.z=e,this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const ql=new k,nh=new _r;class Go{constructor(e=new k(1/0,1/0,1/0),t=new k(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ri.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ri.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ri.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=s.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,ri):ri.fromBufferAttribute(s,o),ri.applyMatrix4(e.matrixWorld),this.expandByPoint(ri);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ra.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ra.copy(n.boundingBox)),ra.applyMatrix4(e.matrixWorld),this.union(ra)}const r=e.children;for(let s=0,o=r.length;s<o;s++)this.expandByObject(r[s],t);return this}containsPoint(e){return!(e.x<this.min.x||e.x>this.max.x||e.y<this.min.y||e.y>this.max.y||e.z<this.min.z||e.z>this.max.z)}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return!(e.max.x<this.min.x||e.min.x>this.max.x||e.max.y<this.min.y||e.min.y>this.max.y||e.max.z<this.min.z||e.min.z>this.max.z)}intersectsSphere(e){return this.clampPoint(e.center,ri),ri.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(co),sa.subVectors(this.max,co),hs.subVectors(e.a,co),ds.subVectors(e.b,co),ps.subVectors(e.c,co),Zi.subVectors(ds,hs),Ji.subVectors(ps,ds),wr.subVectors(hs,ps);let t=[0,-Zi.z,Zi.y,0,-Ji.z,Ji.y,0,-wr.z,wr.y,Zi.z,0,-Zi.x,Ji.z,0,-Ji.x,wr.z,0,-wr.x,-Zi.y,Zi.x,0,-Ji.y,Ji.x,0,-wr.y,wr.x,0];return!Yl(t,hs,ds,ps,sa)||(t=[1,0,0,0,1,0,0,0,1],!Yl(t,hs,ds,ps,sa))?!1:(oa.crossVectors(Zi,Ji),t=[oa.x,oa.y,oa.z],Yl(t,hs,ds,ps,sa))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ri).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ri).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Ai[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Ai[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Ai[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Ai[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Ai[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Ai[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Ai[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Ai[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Ai),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Ai=[new k,new k,new k,new k,new k,new k,new k,new k],ri=new k,ra=new Go,hs=new k,ds=new k,ps=new k,Zi=new k,Ji=new k,wr=new k,co=new k,sa=new k,oa=new k,Rr=new k;function Yl(i,e,t,n,r){for(let s=0,o=i.length-3;s<=o;s+=3){Rr.fromArray(i,s);const a=r.x*Math.abs(Rr.x)+r.y*Math.abs(Rr.y)+r.z*Math.abs(Rr.z),l=e.dot(Rr),c=t.dot(Rr),u=n.dot(Rr);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>a)return!1}return!0}const n_=new Go,uo=new k,jl=new k;class Vo{constructor(e=new k,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):n_.setFromPoints(e).getCenter(n);let r=0;for(let s=0,o=e.length;s<o;s++)r=Math.max(r,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(r),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;uo.subVectors(e,this.center);const t=uo.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),r=(n-this.radius)*.5;this.center.addScaledVector(uo,r/n),this.radius+=r}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(jl.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(uo.copy(e.center).add(jl)),this.expandByPoint(uo.copy(e.center).sub(jl))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const wi=new k,$l=new k,aa=new k,Qi=new k,Kl=new k,la=new k,Zl=new k;class Wo{constructor(e=new k,t=new k(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,wi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=wi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(wi.copy(this.origin).addScaledVector(this.direction,t),wi.distanceToSquared(e))}distanceSqToSegment(e,t,n,r){$l.copy(e).add(t).multiplyScalar(.5),aa.copy(t).sub(e).normalize(),Qi.copy(this.origin).sub($l);const s=e.distanceTo(t)*.5,o=-this.direction.dot(aa),a=Qi.dot(this.direction),l=-Qi.dot(aa),c=Qi.lengthSq(),u=Math.abs(1-o*o);let f,d,m,v;if(u>0)if(f=o*l-a,d=o*a-l,v=s*u,f>=0)if(d>=-v)if(d<=v){const M=1/u;f*=M,d*=M,m=f*(f+o*d+2*a)+d*(o*f+d+2*l)+c}else d=s,f=Math.max(0,-(o*d+a)),m=-f*f+d*(d+2*l)+c;else d=-s,f=Math.max(0,-(o*d+a)),m=-f*f+d*(d+2*l)+c;else d<=-v?(f=Math.max(0,-(-o*s+a)),d=f>0?-s:Math.min(Math.max(-s,-l),s),m=-f*f+d*(d+2*l)+c):d<=v?(f=0,d=Math.min(Math.max(-s,-l),s),m=d*(d+2*l)+c):(f=Math.max(0,-(o*s+a)),d=f>0?s:Math.min(Math.max(-s,-l),s),m=-f*f+d*(d+2*l)+c);else d=o>0?-s:s,f=Math.max(0,-(o*d+a)),m=-f*f+d*(d+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,f),r&&r.copy($l).addScaledVector(aa,d),m}intersectSphere(e,t){wi.subVectors(e.center,this.origin);const n=wi.dot(this.direction),r=wi.dot(wi)-n*n,s=e.radius*e.radius;if(r>s)return null;const o=Math.sqrt(s-r),a=n-o,l=n+o;return l<0?null:a<0?this.at(l,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,r,s,o,a,l;const c=1/this.direction.x,u=1/this.direction.y,f=1/this.direction.z,d=this.origin;return c>=0?(n=(e.min.x-d.x)*c,r=(e.max.x-d.x)*c):(n=(e.max.x-d.x)*c,r=(e.min.x-d.x)*c),u>=0?(s=(e.min.y-d.y)*u,o=(e.max.y-d.y)*u):(s=(e.max.y-d.y)*u,o=(e.min.y-d.y)*u),n>o||s>r||((s>n||isNaN(n))&&(n=s),(o<r||isNaN(r))&&(r=o),f>=0?(a=(e.min.z-d.z)*f,l=(e.max.z-d.z)*f):(a=(e.max.z-d.z)*f,l=(e.min.z-d.z)*f),n>l||a>r)||((a>n||n!==n)&&(n=a),(l<r||r!==r)&&(r=l),r<0)?null:this.at(n>=0?n:r,t)}intersectsBox(e){return this.intersectBox(e,wi)!==null}intersectTriangle(e,t,n,r,s){Kl.subVectors(t,e),la.subVectors(n,e),Zl.crossVectors(Kl,la);let o=this.direction.dot(Zl),a;if(o>0){if(r)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Qi.subVectors(this.origin,e);const l=a*this.direction.dot(la.crossVectors(Qi,la));if(l<0)return null;const c=a*this.direction.dot(Kl.cross(Qi));if(c<0||l+c>o)return null;const u=-a*Qi.dot(Zl);return u<0?null:this.at(u/o,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Bt{constructor(e,t,n,r,s,o,a,l,c,u,f,d,m,v,M,p){Bt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,r,s,o,a,l,c,u,f,d,m,v,M,p)}set(e,t,n,r,s,o,a,l,c,u,f,d,m,v,M,p){const h=this.elements;return h[0]=e,h[4]=t,h[8]=n,h[12]=r,h[1]=s,h[5]=o,h[9]=a,h[13]=l,h[2]=c,h[6]=u,h[10]=f,h[14]=d,h[3]=m,h[7]=v,h[11]=M,h[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Bt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,r=1/ms.setFromMatrixColumn(e,0).length(),s=1/ms.setFromMatrixColumn(e,1).length(),o=1/ms.setFromMatrixColumn(e,2).length();return t[0]=n[0]*r,t[1]=n[1]*r,t[2]=n[2]*r,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,r=e.y,s=e.z,o=Math.cos(n),a=Math.sin(n),l=Math.cos(r),c=Math.sin(r),u=Math.cos(s),f=Math.sin(s);if(e.order==="XYZ"){const d=o*u,m=o*f,v=a*u,M=a*f;t[0]=l*u,t[4]=-l*f,t[8]=c,t[1]=m+v*c,t[5]=d-M*c,t[9]=-a*l,t[2]=M-d*c,t[6]=v+m*c,t[10]=o*l}else if(e.order==="YXZ"){const d=l*u,m=l*f,v=c*u,M=c*f;t[0]=d+M*a,t[4]=v*a-m,t[8]=o*c,t[1]=o*f,t[5]=o*u,t[9]=-a,t[2]=m*a-v,t[6]=M+d*a,t[10]=o*l}else if(e.order==="ZXY"){const d=l*u,m=l*f,v=c*u,M=c*f;t[0]=d-M*a,t[4]=-o*f,t[8]=v+m*a,t[1]=m+v*a,t[5]=o*u,t[9]=M-d*a,t[2]=-o*c,t[6]=a,t[10]=o*l}else if(e.order==="ZYX"){const d=o*u,m=o*f,v=a*u,M=a*f;t[0]=l*u,t[4]=v*c-m,t[8]=d*c+M,t[1]=l*f,t[5]=M*c+d,t[9]=m*c-v,t[2]=-c,t[6]=a*l,t[10]=o*l}else if(e.order==="YZX"){const d=o*l,m=o*c,v=a*l,M=a*c;t[0]=l*u,t[4]=M-d*f,t[8]=v*f+m,t[1]=f,t[5]=o*u,t[9]=-a*u,t[2]=-c*u,t[6]=m*f+v,t[10]=d-M*f}else if(e.order==="XZY"){const d=o*l,m=o*c,v=a*l,M=a*c;t[0]=l*u,t[4]=-f,t[8]=c*u,t[1]=d*f+M,t[5]=o*u,t[9]=m*f-v,t[2]=v*f-m,t[6]=a*u,t[10]=M*f+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(i_,e,r_)}lookAt(e,t,n){const r=this.elements;return Fn.subVectors(e,t),Fn.lengthSq()===0&&(Fn.z=1),Fn.normalize(),er.crossVectors(n,Fn),er.lengthSq()===0&&(Math.abs(n.z)===1?Fn.x+=1e-4:Fn.z+=1e-4,Fn.normalize(),er.crossVectors(n,Fn)),er.normalize(),ca.crossVectors(Fn,er),r[0]=er.x,r[4]=ca.x,r[8]=Fn.x,r[1]=er.y,r[5]=ca.y,r[9]=Fn.y,r[2]=er.z,r[6]=ca.z,r[10]=Fn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,r=t.elements,s=this.elements,o=n[0],a=n[4],l=n[8],c=n[12],u=n[1],f=n[5],d=n[9],m=n[13],v=n[2],M=n[6],p=n[10],h=n[14],x=n[3],_=n[7],y=n[11],D=n[15],b=r[0],R=r[4],q=r[8],T=r[12],A=r[1],I=r[5],Y=r[9],J=r[13],N=r[2],B=r[6],V=r[10],W=r[14],ie=r[3],te=r[7],Q=r[11],ae=r[15];return s[0]=o*b+a*A+l*N+c*ie,s[4]=o*R+a*I+l*B+c*te,s[8]=o*q+a*Y+l*V+c*Q,s[12]=o*T+a*J+l*W+c*ae,s[1]=u*b+f*A+d*N+m*ie,s[5]=u*R+f*I+d*B+m*te,s[9]=u*q+f*Y+d*V+m*Q,s[13]=u*T+f*J+d*W+m*ae,s[2]=v*b+M*A+p*N+h*ie,s[6]=v*R+M*I+p*B+h*te,s[10]=v*q+M*Y+p*V+h*Q,s[14]=v*T+M*J+p*W+h*ae,s[3]=x*b+_*A+y*N+D*ie,s[7]=x*R+_*I+y*B+D*te,s[11]=x*q+_*Y+y*V+D*Q,s[15]=x*T+_*J+y*W+D*ae,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],r=e[8],s=e[12],o=e[1],a=e[5],l=e[9],c=e[13],u=e[2],f=e[6],d=e[10],m=e[14],v=e[3],M=e[7],p=e[11],h=e[15];return v*(+s*l*f-r*c*f-s*a*d+n*c*d+r*a*m-n*l*m)+M*(+t*l*m-t*c*d+s*o*d-r*o*m+r*c*u-s*l*u)+p*(+t*c*f-t*a*m-s*o*f+n*o*m+s*a*u-n*c*u)+h*(-r*a*u-t*l*f+t*a*d+r*o*f-n*o*d+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const r=this.elements;return e.isVector3?(r[12]=e.x,r[13]=e.y,r[14]=e.z):(r[12]=e,r[13]=t,r[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],r=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],f=e[9],d=e[10],m=e[11],v=e[12],M=e[13],p=e[14],h=e[15],x=f*p*c-M*d*c+M*l*m-a*p*m-f*l*h+a*d*h,_=v*d*c-u*p*c-v*l*m+o*p*m+u*l*h-o*d*h,y=u*M*c-v*f*c+v*a*m-o*M*m-u*a*h+o*f*h,D=v*f*l-u*M*l-v*a*d+o*M*d+u*a*p-o*f*p,b=t*x+n*_+r*y+s*D;if(b===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const R=1/b;return e[0]=x*R,e[1]=(M*d*s-f*p*s-M*r*m+n*p*m+f*r*h-n*d*h)*R,e[2]=(a*p*s-M*l*s+M*r*c-n*p*c-a*r*h+n*l*h)*R,e[3]=(f*l*s-a*d*s-f*r*c+n*d*c+a*r*m-n*l*m)*R,e[4]=_*R,e[5]=(u*p*s-v*d*s+v*r*m-t*p*m-u*r*h+t*d*h)*R,e[6]=(v*l*s-o*p*s-v*r*c+t*p*c+o*r*h-t*l*h)*R,e[7]=(o*d*s-u*l*s+u*r*c-t*d*c-o*r*m+t*l*m)*R,e[8]=y*R,e[9]=(v*f*s-u*M*s-v*n*m+t*M*m+u*n*h-t*f*h)*R,e[10]=(o*M*s-v*a*s+v*n*c-t*M*c-o*n*h+t*a*h)*R,e[11]=(u*a*s-o*f*s-u*n*c+t*f*c+o*n*m-t*a*m)*R,e[12]=D*R,e[13]=(u*M*r-v*f*r+v*n*d-t*M*d-u*n*p+t*f*p)*R,e[14]=(v*a*r-o*M*r-v*n*l+t*M*l+o*n*p-t*a*p)*R,e[15]=(o*f*r-u*a*r+u*n*l-t*f*l-o*n*d+t*a*d)*R,this}scale(e){const t=this.elements,n=e.x,r=e.y,s=e.z;return t[0]*=n,t[4]*=r,t[8]*=s,t[1]*=n,t[5]*=r,t[9]*=s,t[2]*=n,t[6]*=r,t[10]*=s,t[3]*=n,t[7]*=r,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],r=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,r))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),r=Math.sin(t),s=1-n,o=e.x,a=e.y,l=e.z,c=s*o,u=s*a;return this.set(c*o+n,c*a-r*l,c*l+r*a,0,c*a+r*l,u*a+n,u*l-r*o,0,c*l-r*a,u*l+r*o,s*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,r,s,o){return this.set(1,n,s,0,e,1,o,0,t,r,1,0,0,0,0,1),this}compose(e,t,n){const r=this.elements,s=t._x,o=t._y,a=t._z,l=t._w,c=s+s,u=o+o,f=a+a,d=s*c,m=s*u,v=s*f,M=o*u,p=o*f,h=a*f,x=l*c,_=l*u,y=l*f,D=n.x,b=n.y,R=n.z;return r[0]=(1-(M+h))*D,r[1]=(m+y)*D,r[2]=(v-_)*D,r[3]=0,r[4]=(m-y)*b,r[5]=(1-(d+h))*b,r[6]=(p+x)*b,r[7]=0,r[8]=(v+_)*R,r[9]=(p-x)*R,r[10]=(1-(d+M))*R,r[11]=0,r[12]=e.x,r[13]=e.y,r[14]=e.z,r[15]=1,this}decompose(e,t,n){const r=this.elements;let s=ms.set(r[0],r[1],r[2]).length();const o=ms.set(r[4],r[5],r[6]).length(),a=ms.set(r[8],r[9],r[10]).length();this.determinant()<0&&(s=-s),e.x=r[12],e.y=r[13],e.z=r[14],si.copy(this);const c=1/s,u=1/o,f=1/a;return si.elements[0]*=c,si.elements[1]*=c,si.elements[2]*=c,si.elements[4]*=u,si.elements[5]*=u,si.elements[6]*=u,si.elements[8]*=f,si.elements[9]*=f,si.elements[10]*=f,t.setFromRotationMatrix(si),n.x=s,n.y=o,n.z=a,this}makePerspective(e,t,n,r,s,o,a=zi){const l=this.elements,c=2*s/(t-e),u=2*s/(n-r),f=(t+e)/(t-e),d=(n+r)/(n-r);let m,v;if(a===zi)m=-(o+s)/(o-s),v=-2*o*s/(o-s);else if(a===Ka)m=-o/(o-s),v=-o*s/(o-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return l[0]=c,l[4]=0,l[8]=f,l[12]=0,l[1]=0,l[5]=u,l[9]=d,l[13]=0,l[2]=0,l[6]=0,l[10]=m,l[14]=v,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,r,s,o,a=zi){const l=this.elements,c=1/(t-e),u=1/(n-r),f=1/(o-s),d=(t+e)*c,m=(n+r)*u;let v,M;if(a===zi)v=(o+s)*f,M=-2*f;else if(a===Ka)v=s*f,M=-1*f;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-d,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-m,l[2]=0,l[6]=0,l[10]=M,l[14]=-v,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let r=0;r<16;r++)if(t[r]!==n[r])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const ms=new k,si=new Bt,i_=new k(0,0,0),r_=new k(1,1,1),er=new k,ca=new k,Fn=new k,ih=new Bt,rh=new _r;class cl{constructor(e=0,t=0,n=0,r=cl.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=r}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,r=this._order){return this._x=e,this._y=t,this._z=n,this._order=r,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const r=e.elements,s=r[0],o=r[4],a=r[8],l=r[1],c=r[5],u=r[9],f=r[2],d=r[6],m=r[10];switch(t){case"XYZ":this._y=Math.asin(En(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,m),this._z=Math.atan2(-o,s)):(this._x=Math.atan2(d,c),this._z=0);break;case"YXZ":this._x=Math.asin(-En(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,m),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-f,s),this._z=0);break;case"ZXY":this._x=Math.asin(En(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-f,m),this._z=Math.atan2(-o,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-En(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(d,m),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-o,c));break;case"YZX":this._z=Math.asin(En(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-f,s)):(this._x=0,this._y=Math.atan2(a,m));break;case"XZY":this._z=Math.asin(-En(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(d,c),this._y=Math.atan2(a,s)):(this._x=Math.atan2(-u,m),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return ih.makeRotationFromQuaternion(e),this.setFromRotationMatrix(ih,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return rh.setFromEuler(this),this.setFromQuaternion(rh,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}cl.DEFAULT_ORDER="XYZ";class Mu{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let s_=0;const sh=new k,gs=new _r,Ri=new Bt,ua=new k,fo=new k,o_=new k,a_=new _r,oh=new k(1,0,0),ah=new k(0,1,0),lh=new k(0,0,1),l_={type:"added"},c_={type:"removed"};class Zt extends jr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:s_++}),this.uuid=ur(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Zt.DEFAULT_UP.clone();const e=new k,t=new cl,n=new _r,r=new k(1,1,1);function s(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:r},modelViewMatrix:{value:new Bt},normalMatrix:{value:new at}}),this.matrix=new Bt,this.matrixWorld=new Bt,this.matrixAutoUpdate=Zt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Zt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Mu,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return gs.setFromAxisAngle(e,t),this.quaternion.multiply(gs),this}rotateOnWorldAxis(e,t){return gs.setFromAxisAngle(e,t),this.quaternion.premultiply(gs),this}rotateX(e){return this.rotateOnAxis(oh,e)}rotateY(e){return this.rotateOnAxis(ah,e)}rotateZ(e){return this.rotateOnAxis(lh,e)}translateOnAxis(e,t){return sh.copy(e).applyQuaternion(this.quaternion),this.position.add(sh.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(oh,e)}translateY(e){return this.translateOnAxis(ah,e)}translateZ(e){return this.translateOnAxis(lh,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Ri.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?ua.copy(e):ua.set(e,t,n);const r=this.parent;this.updateWorldMatrix(!0,!1),fo.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ri.lookAt(fo,ua,this.up):Ri.lookAt(ua,fo,this.up),this.quaternion.setFromRotationMatrix(Ri),r&&(Ri.extractRotation(r.matrixWorld),gs.setFromRotationMatrix(Ri),this.quaternion.premultiply(gs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.parent!==null&&e.parent.remove(e),e.parent=this,this.children.push(e),e.dispatchEvent(l_)):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(c_)),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Ri.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Ri.multiply(e.parent.matrixWorld)),e.applyMatrix4(Ri),this.add(e),e.updateWorldMatrix(!1,!0),this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,r=this.children.length;n<r;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const r=this.children;for(let s=0,o=r.length;s<o;s++)r[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fo,e,o_),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(fo,a_,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,r=t.length;n<r;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,r=t.length;n<r;n++){const s=t[n];(s.matrixWorldAutoUpdate===!0||e===!0)&&s.updateMatrixWorld(e)}}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.matrixWorldAutoUpdate===!0&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix),t===!0){const r=this.children;for(let s=0,o=r.length;s<o;s++){const a=r[s];a.matrixWorldAutoUpdate===!0&&a.updateWorldMatrix(!1,!0)}}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const r={};r.uuid=this.uuid,r.type=this.type,this.name!==""&&(r.name=this.name),this.castShadow===!0&&(r.castShadow=!0),this.receiveShadow===!0&&(r.receiveShadow=!0),this.visible===!1&&(r.visible=!1),this.frustumCulled===!1&&(r.frustumCulled=!1),this.renderOrder!==0&&(r.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(r.userData=this.userData),r.layers=this.layers.mask,r.matrix=this.matrix.toArray(),r.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(r.matrixAutoUpdate=!1),this.isInstancedMesh&&(r.type="InstancedMesh",r.count=this.count,r.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(r.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(r.type="BatchedMesh",r.perObjectFrustumCulled=this.perObjectFrustumCulled,r.sortObjects=this.sortObjects,r.drawRanges=this._drawRanges,r.reservedRanges=this._reservedRanges,r.visibility=this._visibility,r.active=this._active,r.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),r.maxGeometryCount=this._maxGeometryCount,r.maxVertexCount=this._maxVertexCount,r.maxIndexCount=this._maxIndexCount,r.geometryInitialized=this._geometryInitialized,r.geometryCount=this._geometryCount,r.matricesTexture=this._matricesTexture.toJSON(e),this.boundingSphere!==null&&(r.boundingSphere={center:r.boundingSphere.center.toArray(),radius:r.boundingSphere.radius}),this.boundingBox!==null&&(r.boundingBox={min:r.boundingBox.min.toArray(),max:r.boundingBox.max.toArray()}));function s(a,l){return a[l.uuid]===void 0&&(a[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?r.background=this.background.toJSON():this.background.isTexture&&(r.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(r.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){r.geometry=s(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const l=a.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const f=l[c];s(e.shapes,f)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(r.bindMode=this.bindMode,r.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),r.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let l=0,c=this.material.length;l<c;l++)a.push(s(e.materials,this.material[l]));r.material=a}else r.material=s(e.materials,this.material);if(this.children.length>0){r.children=[];for(let a=0;a<this.children.length;a++)r.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){r.animations=[];for(let a=0;a<this.animations.length;a++){const l=this.animations[a];r.animations.push(s(e.animations,l))}}if(t){const a=o(e.geometries),l=o(e.materials),c=o(e.textures),u=o(e.images),f=o(e.shapes),d=o(e.skeletons),m=o(e.animations),v=o(e.nodes);a.length>0&&(n.geometries=a),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),f.length>0&&(n.shapes=f),d.length>0&&(n.skeletons=d),m.length>0&&(n.animations=m),v.length>0&&(n.nodes=v)}return n.object=r,n;function o(a){const l=[];for(const c in a){const u=a[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const r=e.children[n];this.add(r.clone())}return this}}Zt.DEFAULT_UP=new k(0,1,0);Zt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Zt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const oi=new k,Ci=new k,Jl=new k,Li=new k,_s=new k,vs=new k,ch=new k,Ql=new k,ec=new k,tc=new k;let fa=!1;class Zn{constructor(e=new k,t=new k,n=new k){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,r){r.subVectors(n,t),oi.subVectors(e,t),r.cross(oi);const s=r.lengthSq();return s>0?r.multiplyScalar(1/Math.sqrt(s)):r.set(0,0,0)}static getBarycoord(e,t,n,r,s){oi.subVectors(r,t),Ci.subVectors(n,t),Jl.subVectors(e,t);const o=oi.dot(oi),a=oi.dot(Ci),l=oi.dot(Jl),c=Ci.dot(Ci),u=Ci.dot(Jl),f=o*c-a*a;if(f===0)return s.set(0,0,0),null;const d=1/f,m=(c*l-a*u)*d,v=(o*u-a*l)*d;return s.set(1-m-v,v,m)}static containsPoint(e,t,n,r){return this.getBarycoord(e,t,n,r,Li)===null?!1:Li.x>=0&&Li.y>=0&&Li.x+Li.y<=1}static getUV(e,t,n,r,s,o,a,l){return fa===!1&&(console.warn("THREE.Triangle.getUV() has been renamed to THREE.Triangle.getInterpolation()."),fa=!0),this.getInterpolation(e,t,n,r,s,o,a,l)}static getInterpolation(e,t,n,r,s,o,a,l){return this.getBarycoord(e,t,n,r,Li)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,Li.x),l.addScaledVector(o,Li.y),l.addScaledVector(a,Li.z),l)}static isFrontFacing(e,t,n,r){return oi.subVectors(n,t),Ci.subVectors(e,t),oi.cross(Ci).dot(r)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,r){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[r]),this}setFromAttributeAndIndices(e,t,n,r){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,r),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return oi.subVectors(this.c,this.b),Ci.subVectors(this.a,this.b),oi.cross(Ci).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Zn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Zn.getBarycoord(e,this.a,this.b,this.c,t)}getUV(e,t,n,r,s){return fa===!1&&(console.warn("THREE.Triangle.getUV() has been renamed to THREE.Triangle.getInterpolation()."),fa=!0),Zn.getInterpolation(e,this.a,this.b,this.c,t,n,r,s)}getInterpolation(e,t,n,r,s){return Zn.getInterpolation(e,this.a,this.b,this.c,t,n,r,s)}containsPoint(e){return Zn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Zn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,r=this.b,s=this.c;let o,a;_s.subVectors(r,n),vs.subVectors(s,n),Ql.subVectors(e,n);const l=_s.dot(Ql),c=vs.dot(Ql);if(l<=0&&c<=0)return t.copy(n);ec.subVectors(e,r);const u=_s.dot(ec),f=vs.dot(ec);if(u>=0&&f<=u)return t.copy(r);const d=l*f-u*c;if(d<=0&&l>=0&&u<=0)return o=l/(l-u),t.copy(n).addScaledVector(_s,o);tc.subVectors(e,s);const m=_s.dot(tc),v=vs.dot(tc);if(v>=0&&m<=v)return t.copy(s);const M=m*c-l*v;if(M<=0&&c>=0&&v<=0)return a=c/(c-v),t.copy(n).addScaledVector(vs,a);const p=u*v-m*f;if(p<=0&&f-u>=0&&m-v>=0)return ch.subVectors(s,r),a=(f-u)/(f-u+(m-v)),t.copy(r).addScaledVector(ch,a);const h=1/(p+M+d);return o=M*h,a=d*h,t.copy(n).addScaledVector(_s,o).addScaledVector(vs,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const dp={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},tr={h:0,s:0,l:0},ha={h:0,s:0,l:0};function nc(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class ft{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const r=e;r&&r.isColor?this.copy(r):typeof r=="number"?this.setHex(r):typeof r=="string"&&this.setStyle(r)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=fn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Tt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,r=Tt.workingColorSpace){return this.r=e,this.g=t,this.b=n,Tt.toWorkingColorSpace(this,r),this}setHSL(e,t,n,r=Tt.workingColorSpace){if(e=jg(e,1),t=En(t,0,1),n=En(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,o=2*n-s;this.r=nc(o,s,e+1/3),this.g=nc(o,s,e),this.b=nc(o,s,e-1/3)}return Tt.toWorkingColorSpace(this,r),this}setStyle(e,t=fn){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let r;if(r=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const o=r[1],a=r[2];switch(o){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(r=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=r[1],o=s.length;if(o===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=fn){const n=dp[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Os(e.r),this.g=Os(e.g),this.b=Os(e.b),this}copyLinearToSRGB(e){return this.r=Wl(e.r),this.g=Wl(e.g),this.b=Wl(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=fn){return Tt.fromWorkingColorSpace(pn.copy(this),e),Math.round(En(pn.r*255,0,255))*65536+Math.round(En(pn.g*255,0,255))*256+Math.round(En(pn.b*255,0,255))}getHexString(e=fn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Tt.workingColorSpace){Tt.fromWorkingColorSpace(pn.copy(this),t);const n=pn.r,r=pn.g,s=pn.b,o=Math.max(n,r,s),a=Math.min(n,r,s);let l,c;const u=(a+o)/2;if(a===o)l=0,c=0;else{const f=o-a;switch(c=u<=.5?f/(o+a):f/(2-o-a),o){case n:l=(r-s)/f+(r<s?6:0);break;case r:l=(s-n)/f+2;break;case s:l=(n-r)/f+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=Tt.workingColorSpace){return Tt.fromWorkingColorSpace(pn.copy(this),t),e.r=pn.r,e.g=pn.g,e.b=pn.b,e}getStyle(e=fn){Tt.fromWorkingColorSpace(pn.copy(this),e);const t=pn.r,n=pn.g,r=pn.b;return e!==fn?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${r.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(r*255)})`}offsetHSL(e,t,n){return this.getHSL(tr),this.setHSL(tr.h+e,tr.s+t,tr.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(tr),e.getHSL(ha);const n=Gl(tr.h,ha.h,t),r=Gl(tr.s,ha.s,t),s=Gl(tr.l,ha.l,t);return this.setHSL(n,r,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,r=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*r,this.g=s[1]*t+s[4]*n+s[7]*r,this.b=s[2]*t+s[5]*n+s[8]*r,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const pn=new ft;ft.NAMES=dp;let u_=0;class $r extends jr{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:u_++}),this.uuid=ur(),this.name="",this.type="Material",this.blending=Fs,this.side=gr,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Yc,this.blendDst=jc,this.blendEquation=Fr,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new ft(0,0,0),this.blendAlpha=0,this.depthFunc=qa,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Kf,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=us,this.stencilZFail=us,this.stencilZPass=us,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBuild(){}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const r=this[t];if(r===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}r&&r.isColor?r.set(n):r&&r.isVector3&&n&&n.isVector3?r.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Fs&&(n.blending=this.blending),this.side!==gr&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==Yc&&(n.blendSrc=this.blendSrc),this.blendDst!==jc&&(n.blendDst=this.blendDst),this.blendEquation!==Fr&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==qa&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Kf&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==us&&(n.stencilFail=this.stencilFail),this.stencilZFail!==us&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==us&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function r(s){const o=[];for(const a in s){const l=s[a];delete l.metadata,o.push(l)}return o}if(t){const s=r(e.textures),o=r(e.images);s.length>0&&(n.textures=s),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const r=t.length;n=new Array(r);for(let s=0;s!==r;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}}class ul extends $r{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new ft(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.combine=Jd,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Xt=new k,da=new qe;class Gn{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Qc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.gpuType=or,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return console.warn("THREE.BufferAttribute: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let r=0,s=this.itemSize;r<s;r++)this.array[e+r]=t.array[n+r];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)da.fromBufferAttribute(this,t),da.applyMatrix3(e),this.setXY(t,da.x,da.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix3(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyMatrix4(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.applyNormalMatrix(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Xt.fromBufferAttribute(this,t),Xt.transformDirection(e),this.setXYZ(t,Xt.x,Xt.y,Xt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=Oi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=At(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Oi(t,this.array)),t}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Oi(t,this.array)),t}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Oi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Oi(t,this.array)),t}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,r){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),r=At(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e*=this.itemSize,this.normalized&&(t=At(t,this.array),n=At(n,this.array),r=At(r,this.array),s=At(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=r,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Qc&&(e.usage=this.usage),e}}class pp extends Gn{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class mp extends Gn{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Ot extends Gn{constructor(e,t,n){super(new Float32Array(e),t,n)}}let f_=0;const Yn=new Bt,ic=new Zt,xs=new k,On=new Go,ho=new Go,on=new k;class An extends jr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:f_++}),this.uuid=ur(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(cp(e)?mp:pp)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new at().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const r=this.attributes.tangent;return r!==void 0&&(r.transformDirection(e),r.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Yn.makeRotationFromQuaternion(e),this.applyMatrix4(Yn),this}rotateX(e){return Yn.makeRotationX(e),this.applyMatrix4(Yn),this}rotateY(e){return Yn.makeRotationY(e),this.applyMatrix4(Yn),this}rotateZ(e){return Yn.makeRotationZ(e),this.applyMatrix4(Yn),this}translate(e,t,n){return Yn.makeTranslation(e,t,n),this.applyMatrix4(Yn),this}scale(e,t,n){return Yn.makeScale(e,t,n),this.applyMatrix4(Yn),this}lookAt(e){return ic.lookAt(e),ic.updateMatrix(),this.applyMatrix4(ic.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(xs).negate(),this.translate(xs.x,xs.y,xs.z),this}setFromPoints(e){const t=[];for(let n=0,r=e.length;n<r;n++){const s=e[n];t.push(s.x,s.y,s.z||0)}return this.setAttribute("position",new Ot(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Go);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error('THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box. Alternatively set "mesh.frustumCulled" to "false".',this),this.boundingBox.set(new k(-1/0,-1/0,-1/0),new k(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,r=t.length;n<r;n++){const s=t[n];On.setFromBufferAttribute(s),this.morphTargetsRelative?(on.addVectors(this.boundingBox.min,On.min),this.boundingBox.expandByPoint(on),on.addVectors(this.boundingBox.max,On.max),this.boundingBox.expandByPoint(on)):(this.boundingBox.expandByPoint(On.min),this.boundingBox.expandByPoint(On.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Vo);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error('THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere. Alternatively set "mesh.frustumCulled" to "false".',this),this.boundingSphere.set(new k,1/0);return}if(e){const n=this.boundingSphere.center;if(On.setFromBufferAttribute(e),t)for(let s=0,o=t.length;s<o;s++){const a=t[s];ho.setFromBufferAttribute(a),this.morphTargetsRelative?(on.addVectors(On.min,ho.min),On.expandByPoint(on),on.addVectors(On.max,ho.max),On.expandByPoint(on)):(On.expandByPoint(ho.min),On.expandByPoint(ho.max))}On.getCenter(n);let r=0;for(let s=0,o=e.count;s<o;s++)on.fromBufferAttribute(e,s),r=Math.max(r,n.distanceToSquared(on));if(t)for(let s=0,o=t.length;s<o;s++){const a=t[s],l=this.morphTargetsRelative;for(let c=0,u=a.count;c<u;c++)on.fromBufferAttribute(a,c),l&&(xs.fromBufferAttribute(e,c),on.add(xs)),r=Math.max(r,n.distanceToSquared(on))}this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=e.array,r=t.position.array,s=t.normal.array,o=t.uv.array,a=r.length/3;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Gn(new Float32Array(4*a),4));const l=this.getAttribute("tangent").array,c=[],u=[];for(let A=0;A<a;A++)c[A]=new k,u[A]=new k;const f=new k,d=new k,m=new k,v=new qe,M=new qe,p=new qe,h=new k,x=new k;function _(A,I,Y){f.fromArray(r,A*3),d.fromArray(r,I*3),m.fromArray(r,Y*3),v.fromArray(o,A*2),M.fromArray(o,I*2),p.fromArray(o,Y*2),d.sub(f),m.sub(f),M.sub(v),p.sub(v);const J=1/(M.x*p.y-p.x*M.y);isFinite(J)&&(h.copy(d).multiplyScalar(p.y).addScaledVector(m,-M.y).multiplyScalar(J),x.copy(m).multiplyScalar(M.x).addScaledVector(d,-p.x).multiplyScalar(J),c[A].add(h),c[I].add(h),c[Y].add(h),u[A].add(x),u[I].add(x),u[Y].add(x))}let y=this.groups;y.length===0&&(y=[{start:0,count:n.length}]);for(let A=0,I=y.length;A<I;++A){const Y=y[A],J=Y.start,N=Y.count;for(let B=J,V=J+N;B<V;B+=3)_(n[B+0],n[B+1],n[B+2])}const D=new k,b=new k,R=new k,q=new k;function T(A){R.fromArray(s,A*3),q.copy(R);const I=c[A];D.copy(I),D.sub(R.multiplyScalar(R.dot(I))).normalize(),b.crossVectors(q,I);const J=b.dot(u[A])<0?-1:1;l[A*4]=D.x,l[A*4+1]=D.y,l[A*4+2]=D.z,l[A*4+3]=J}for(let A=0,I=y.length;A<I;++A){const Y=y[A],J=Y.start,N=Y.count;for(let B=J,V=J+N;B<V;B+=3)T(n[B+0]),T(n[B+1]),T(n[B+2])}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Gn(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,m=n.count;d<m;d++)n.setXYZ(d,0,0,0);const r=new k,s=new k,o=new k,a=new k,l=new k,c=new k,u=new k,f=new k;if(e)for(let d=0,m=e.count;d<m;d+=3){const v=e.getX(d+0),M=e.getX(d+1),p=e.getX(d+2);r.fromBufferAttribute(t,v),s.fromBufferAttribute(t,M),o.fromBufferAttribute(t,p),u.subVectors(o,s),f.subVectors(r,s),u.cross(f),a.fromBufferAttribute(n,v),l.fromBufferAttribute(n,M),c.fromBufferAttribute(n,p),a.add(u),l.add(u),c.add(u),n.setXYZ(v,a.x,a.y,a.z),n.setXYZ(M,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let d=0,m=t.count;d<m;d+=3)r.fromBufferAttribute(t,d+0),s.fromBufferAttribute(t,d+1),o.fromBufferAttribute(t,d+2),u.subVectors(o,s),f.subVectors(r,s),u.cross(f),n.setXYZ(d+0,u.x,u.y,u.z),n.setXYZ(d+1,u.x,u.y,u.z),n.setXYZ(d+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)on.fromBufferAttribute(e,t),on.normalize(),e.setXYZ(t,on.x,on.y,on.z)}toNonIndexed(){function e(a,l){const c=a.array,u=a.itemSize,f=a.normalized,d=new c.constructor(l.length*u);let m=0,v=0;for(let M=0,p=l.length;M<p;M++){a.isInterleavedBufferAttribute?m=l[M]*a.data.stride+a.offset:m=l[M]*u;for(let h=0;h<u;h++)d[v++]=c[m++]}return new Gn(d,u,f)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new An,n=this.index.array,r=this.attributes;for(const a in r){const l=r[a],c=e(l,n);t.setAttribute(a,c)}const s=this.morphAttributes;for(const a in s){const l=[],c=s[a];for(let u=0,f=c.length;u<f;u++){const d=c[u],m=e(d,n);l.push(m)}t.morphAttributes[a]=l}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,l=o.length;a<l;a++){const c=o[a];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const r={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let f=0,d=c.length;f<d;f++){const m=c[f];u.push(m.toJSON(e.data))}u.length>0&&(r[l]=u,s=!0)}s&&(e.data.morphAttributes=r,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const r=e.attributes;for(const c in r){const u=r[c];this.setAttribute(c,u.clone(t))}const s=e.morphAttributes;for(const c in s){const u=[],f=s[c];for(let d=0,m=f.length;d<m;d++)u.push(f[d].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let c=0,u=o.length;c<u;c++){const f=o[c];this.addGroup(f.start,f.count,f.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const uh=new Bt,Cr=new Wo,pa=new Vo,fh=new k,Ms=new k,Ss=new k,ys=new k,rc=new k,ma=new k,ga=new qe,_a=new qe,va=new qe,hh=new k,dh=new k,ph=new k,xa=new k,Ma=new k;class Mi extends Zt{constructor(e=new An,t=new ul){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=r.length;s<o;s++){const a=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}getVertexPosition(e,t){const n=this.geometry,r=n.attributes.position,s=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(r,e);const a=this.morphTargetInfluences;if(s&&a){ma.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=a[l],f=s[l];u!==0&&(rc.fromBufferAttribute(f,e),o?ma.addScaledVector(rc,u):ma.addScaledVector(rc.sub(t),u))}t.add(ma)}return t}raycast(e,t){const n=this.geometry,r=this.material,s=this.matrixWorld;r!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),pa.copy(n.boundingSphere),pa.applyMatrix4(s),Cr.copy(e.ray).recast(e.near),!(pa.containsPoint(Cr.origin)===!1&&(Cr.intersectSphere(pa,fh)===null||Cr.origin.distanceToSquared(fh)>(e.far-e.near)**2))&&(uh.copy(s).invert(),Cr.copy(e.ray).applyMatrix4(uh),!(n.boundingBox!==null&&Cr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Cr)))}_computeIntersections(e,t,n){let r;const s=this.geometry,o=this.material,a=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,f=s.attributes.normal,d=s.groups,m=s.drawRange;if(a!==null)if(Array.isArray(o))for(let v=0,M=d.length;v<M;v++){const p=d[v],h=o[p.materialIndex],x=Math.max(p.start,m.start),_=Math.min(a.count,Math.min(p.start+p.count,m.start+m.count));for(let y=x,D=_;y<D;y+=3){const b=a.getX(y),R=a.getX(y+1),q=a.getX(y+2);r=Sa(this,h,e,n,c,u,f,b,R,q),r&&(r.faceIndex=Math.floor(y/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const v=Math.max(0,m.start),M=Math.min(a.count,m.start+m.count);for(let p=v,h=M;p<h;p+=3){const x=a.getX(p),_=a.getX(p+1),y=a.getX(p+2);r=Sa(this,o,e,n,c,u,f,x,_,y),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}else if(l!==void 0)if(Array.isArray(o))for(let v=0,M=d.length;v<M;v++){const p=d[v],h=o[p.materialIndex],x=Math.max(p.start,m.start),_=Math.min(l.count,Math.min(p.start+p.count,m.start+m.count));for(let y=x,D=_;y<D;y+=3){const b=y,R=y+1,q=y+2;r=Sa(this,h,e,n,c,u,f,b,R,q),r&&(r.faceIndex=Math.floor(y/3),r.face.materialIndex=p.materialIndex,t.push(r))}}else{const v=Math.max(0,m.start),M=Math.min(l.count,m.start+m.count);for(let p=v,h=M;p<h;p+=3){const x=p,_=p+1,y=p+2;r=Sa(this,o,e,n,c,u,f,x,_,y),r&&(r.faceIndex=Math.floor(p/3),t.push(r))}}}}function h_(i,e,t,n,r,s,o,a){let l;if(e.side===Ln?l=n.intersectTriangle(o,s,r,!0,a):l=n.intersectTriangle(r,s,o,e.side===gr,a),l===null)return null;Ma.copy(a),Ma.applyMatrix4(i.matrixWorld);const c=t.ray.origin.distanceTo(Ma);return c<t.near||c>t.far?null:{distance:c,point:Ma.clone(),object:i}}function Sa(i,e,t,n,r,s,o,a,l,c){i.getVertexPosition(a,Ms),i.getVertexPosition(l,Ss),i.getVertexPosition(c,ys);const u=h_(i,e,t,n,Ms,Ss,ys,xa);if(u){r&&(ga.fromBufferAttribute(r,a),_a.fromBufferAttribute(r,l),va.fromBufferAttribute(r,c),u.uv=Zn.getInterpolation(xa,Ms,Ss,ys,ga,_a,va,new qe)),s&&(ga.fromBufferAttribute(s,a),_a.fromBufferAttribute(s,l),va.fromBufferAttribute(s,c),u.uv1=Zn.getInterpolation(xa,Ms,Ss,ys,ga,_a,va,new qe),u.uv2=u.uv1),o&&(hh.fromBufferAttribute(o,a),dh.fromBufferAttribute(o,l),ph.fromBufferAttribute(o,c),u.normal=Zn.getInterpolation(xa,Ms,Ss,ys,hh,dh,ph,new k),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const f={a,b:l,c,normal:new k,materialIndex:0};Zn.getNormal(Ms,Ss,ys,f.normal),u.face=f}return u}class Xo extends An{constructor(e=1,t=1,n=1,r=1,s=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:r,heightSegments:s,depthSegments:o};const a=this;r=Math.floor(r),s=Math.floor(s),o=Math.floor(o);const l=[],c=[],u=[],f=[];let d=0,m=0;v("z","y","x",-1,-1,n,t,e,o,s,0),v("z","y","x",1,-1,n,t,-e,o,s,1),v("x","z","y",1,1,e,n,t,r,o,2),v("x","z","y",1,-1,e,n,-t,r,o,3),v("x","y","z",1,-1,e,t,n,r,s,4),v("x","y","z",-1,-1,e,t,-n,r,s,5),this.setIndex(l),this.setAttribute("position",new Ot(c,3)),this.setAttribute("normal",new Ot(u,3)),this.setAttribute("uv",new Ot(f,2));function v(M,p,h,x,_,y,D,b,R,q,T){const A=y/R,I=D/q,Y=y/2,J=D/2,N=b/2,B=R+1,V=q+1;let W=0,ie=0;const te=new k;for(let Q=0;Q<V;Q++){const ae=Q*I-J;for(let re=0;re<B;re++){const z=re*A-Y;te[M]=z*x,te[p]=ae*_,te[h]=N,c.push(te.x,te.y,te.z),te[M]=0,te[p]=0,te[h]=b>0?1:-1,u.push(te.x,te.y,te.z),f.push(re/R),f.push(1-Q/q),W+=1}}for(let Q=0;Q<q;Q++)for(let ae=0;ae<R;ae++){const re=d+ae+B*Q,z=d+ae+B*(Q+1),se=d+(ae+1)+B*(Q+1),ve=d+(ae+1)+B*Q;l.push(re,z,ve),l.push(z,se,ve),ie+=6}a.addGroup(m,ie,T),m+=ie,d+=W}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Xo(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Vs(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const r=i[t][n];r&&(r.isColor||r.isMatrix3||r.isMatrix4||r.isVector2||r.isVector3||r.isVector4||r.isTexture||r.isQuaternion)?r.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=r.clone():Array.isArray(r)?e[t][n]=r.slice():e[t][n]=r}}return e}function Mn(i){const e={};for(let t=0;t<i.length;t++){const n=Vs(i[t]);for(const r in n)e[r]=n[r]}return e}function d_(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function gp(i){return i.getRenderTarget()===null?i.outputColorSpace:Tt.workingColorSpace}const p_={clone:Vs,merge:Mn};var m_=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,g_=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class qr extends $r{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=m_,this.fragmentShader=g_,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={derivatives:!1,fragDepth:!1,drawBuffers:!1,shaderTextureLOD:!1,clipCullDistance:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Vs(e.uniforms),this.uniformsGroups=d_(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const r in this.uniforms){const o=this.uniforms[r].value;o&&o.isTexture?t.uniforms[r]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[r]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[r]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[r]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[r]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[r]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[r]={type:"m4",value:o.toArray()}:t.uniforms[r]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const r in this.extensions)this.extensions[r]===!0&&(n[r]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class _p extends Zt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Bt,this.projectionMatrix=new Bt,this.projectionMatrixInverse=new Bt,this.coordinateSystem=zi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}class Jn extends _p{constructor(e=50,t=1,n=.1,r=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=r,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=tu*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ga*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return tu*2*Math.atan(Math.tan(Ga*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}setViewOffset(e,t,n,r,s,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ga*.5*this.fov)/this.zoom,n=2*t,r=this.aspect*n,s=-.5*r;const o=this.view;if(this.view!==null&&this.view.enabled){const l=o.fullWidth,c=o.fullHeight;s+=o.offsetX*r/l,t-=o.offsetY*n/c,r*=o.width/l,n*=o.height/c}const a=this.filmOffset;a!==0&&(s+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+r,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Es=-90,Ts=1;class __ extends Zt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const r=new Jn(Es,Ts,e,t);r.layers=this.layers,this.add(r);const s=new Jn(Es,Ts,e,t);s.layers=this.layers,this.add(s);const o=new Jn(Es,Ts,e,t);o.layers=this.layers,this.add(o);const a=new Jn(Es,Ts,e,t);a.layers=this.layers,this.add(a);const l=new Jn(Es,Ts,e,t);l.layers=this.layers,this.add(l);const c=new Jn(Es,Ts,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,r,s,o,a,l]=t;for(const c of t)this.remove(c);if(e===zi)n.up.set(0,1,0),n.lookAt(1,0,0),r.up.set(0,1,0),r.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===Ka)n.up.set(0,-1,0),n.lookAt(-1,0,0),r.up.set(0,-1,0),r.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:r}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,o,a,l,c,u]=this.children,f=e.getRenderTarget(),d=e.getActiveCubeFace(),m=e.getActiveMipmapLevel(),v=e.xr.enabled;e.xr.enabled=!1;const M=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,r),e.render(t,s),e.setRenderTarget(n,1,r),e.render(t,o),e.setRenderTarget(n,2,r),e.render(t,a),e.setRenderTarget(n,3,r),e.render(t,l),e.setRenderTarget(n,4,r),e.render(t,c),n.texture.generateMipmaps=M,e.setRenderTarget(n,5,r),e.render(t,u),e.setRenderTarget(f,d,m),e.xr.enabled=v,n.texture.needsPMREMUpdate=!0}}class vp extends Pn{constructor(e,t,n,r,s,o,a,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:ks,super(e,t,n,r,s,o,a,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class v_ extends Xr{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},r=[n,n,n,n,n,n];t.encoding!==void 0&&(Lo("THREE.WebGLCubeRenderTarget: option.encoding has been replaced by option.colorSpace."),t.colorSpace=t.encoding===Gr?fn:Qn),this.texture=new vp(r,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Kn}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},r=new Xo(5,5,5),s=new qr({name:"CubemapFromEquirect",uniforms:Vs(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Ln,blending:ar});s.uniforms.tEquirect.value=t;const o=new Mi(r,s),a=t.minFilter;return t.minFilter===No&&(t.minFilter=Kn),new __(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,r){const s=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,r);e.setRenderTarget(s)}}const sc=new k,x_=new k,M_=new at;class ir{constructor(e=new k(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,r){return this.normal.set(e,t,n),this.constant=r,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const r=sc.subVectors(n,t).cross(x_.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(r,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(sc),r=this.normal.dot(n);if(r===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/r;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||M_.getNormalMatrix(e),r=this.coplanarPoint(sc).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-r.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Lr=new Vo,ya=new k;class Su{constructor(e=new ir,t=new ir,n=new ir,r=new ir,s=new ir,o=new ir){this.planes=[e,t,n,r,s,o]}set(e,t,n,r,s,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(r),a[4].copy(s),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=zi){const n=this.planes,r=e.elements,s=r[0],o=r[1],a=r[2],l=r[3],c=r[4],u=r[5],f=r[6],d=r[7],m=r[8],v=r[9],M=r[10],p=r[11],h=r[12],x=r[13],_=r[14],y=r[15];if(n[0].setComponents(l-s,d-c,p-m,y-h).normalize(),n[1].setComponents(l+s,d+c,p+m,y+h).normalize(),n[2].setComponents(l+o,d+u,p+v,y+x).normalize(),n[3].setComponents(l-o,d-u,p-v,y-x).normalize(),n[4].setComponents(l-a,d-f,p-M,y-_).normalize(),t===zi)n[5].setComponents(l+a,d+f,p+M,y+_).normalize();else if(t===Ka)n[5].setComponents(a,f,M,_).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Lr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Lr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Lr)}intersectsSprite(e){return Lr.center.set(0,0,0),Lr.radius=.7071067811865476,Lr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Lr)}intersectsSphere(e){const t=this.planes,n=e.center,r=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<r)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const r=t[n];if(ya.x=r.normal.x>0?e.max.x:e.min.x,ya.y=r.normal.y>0?e.max.y:e.min.y,ya.z=r.normal.z>0?e.max.z:e.min.z,r.distanceToPoint(ya)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function xp(){let i=null,e=!1,t=null,n=null;function r(s,o){t(s,o),n=i.requestAnimationFrame(r)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(r),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){i=s}}}function S_(i,e){const t=e.isWebGL2,n=new WeakMap;function r(c,u){const f=c.array,d=c.usage,m=f.byteLength,v=i.createBuffer();i.bindBuffer(u,v),i.bufferData(u,f,d),c.onUploadCallback();let M;if(f instanceof Float32Array)M=i.FLOAT;else if(f instanceof Uint16Array)if(c.isFloat16BufferAttribute)if(t)M=i.HALF_FLOAT;else throw new Error("THREE.WebGLAttributes: Usage of Float16BufferAttribute requires WebGL2.");else M=i.UNSIGNED_SHORT;else if(f instanceof Int16Array)M=i.SHORT;else if(f instanceof Uint32Array)M=i.UNSIGNED_INT;else if(f instanceof Int32Array)M=i.INT;else if(f instanceof Int8Array)M=i.BYTE;else if(f instanceof Uint8Array)M=i.UNSIGNED_BYTE;else if(f instanceof Uint8ClampedArray)M=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+f);return{buffer:v,type:M,bytesPerElement:f.BYTES_PER_ELEMENT,version:c.version,size:m}}function s(c,u,f){const d=u.array,m=u._updateRange,v=u.updateRanges;if(i.bindBuffer(f,c),m.count===-1&&v.length===0&&i.bufferSubData(f,0,d),v.length!==0){for(let M=0,p=v.length;M<p;M++){const h=v[M];t?i.bufferSubData(f,h.start*d.BYTES_PER_ELEMENT,d,h.start,h.count):i.bufferSubData(f,h.start*d.BYTES_PER_ELEMENT,d.subarray(h.start,h.start+h.count))}u.clearUpdateRanges()}m.count!==-1&&(t?i.bufferSubData(f,m.offset*d.BYTES_PER_ELEMENT,d,m.offset,m.count):i.bufferSubData(f,m.offset*d.BYTES_PER_ELEMENT,d.subarray(m.offset,m.offset+m.count)),m.count=-1),u.onUploadCallback()}function o(c){return c.isInterleavedBufferAttribute&&(c=c.data),n.get(c)}function a(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=n.get(c);u&&(i.deleteBuffer(u.buffer),n.delete(c))}function l(c,u){if(c.isGLBufferAttribute){const d=n.get(c);(!d||d.version<c.version)&&n.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}c.isInterleavedBufferAttribute&&(c=c.data);const f=n.get(c);if(f===void 0)n.set(c,r(c,u));else if(f.version<c.version){if(f.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");s(f.buffer,c,u),f.version=c.version}}return{get:o,remove:a,update:l}}class yu extends An{constructor(e=1,t=1,n=1,r=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:r};const s=e/2,o=t/2,a=Math.floor(n),l=Math.floor(r),c=a+1,u=l+1,f=e/a,d=t/l,m=[],v=[],M=[],p=[];for(let h=0;h<u;h++){const x=h*d-o;for(let _=0;_<c;_++){const y=_*f-s;v.push(y,-x,0),M.push(0,0,1),p.push(_/a),p.push(1-h/l)}}for(let h=0;h<l;h++)for(let x=0;x<a;x++){const _=x+c*h,y=x+c*(h+1),D=x+1+c*(h+1),b=x+1+c*h;m.push(_,y,b),m.push(y,D,b)}this.setIndex(m),this.setAttribute("position",new Ot(v,3)),this.setAttribute("normal",new Ot(M,3)),this.setAttribute("uv",new Ot(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new yu(e.width,e.height,e.widthSegments,e.heightSegments)}}var y_=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,E_=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,T_=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,b_=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,A_=`#ifdef USE_ALPHATEST
	if ( diffuseColor.a < alphaTest ) discard;
#endif`,w_=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,R_=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,C_=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,L_=`#ifdef USE_BATCHING
	attribute float batchId;
	uniform highp sampler2D batchingTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,P_=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( batchId );
#endif`,D_=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,U_=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,I_=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,N_=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,F_=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,O_=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#pragma unroll_loop_start
	for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
		plane = clippingPlanes[ i ];
		if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
	}
	#pragma unroll_loop_end
	#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
		bool clipped = true;
		#pragma unroll_loop_start
		for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
		}
		#pragma unroll_loop_end
		if ( clipped ) discard;
	#endif
#endif`,B_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,z_=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,k_=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,H_=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,G_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,V_=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR )
	varying vec3 vColor;
#endif`,W_=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif`,X_=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
float luminance( const in vec3 rgb ) {
	const vec3 weights = vec3( 0.2126729, 0.7151522, 0.0721750 );
	return dot( weights, rgb );
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,q_=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,Y_=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,j_=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,$_=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,K_=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Z_=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,J_="gl_FragColor = linearToOutputTexel( gl_FragColor );",Q_=`
const mat3 LINEAR_SRGB_TO_LINEAR_DISPLAY_P3 = mat3(
	vec3( 0.8224621, 0.177538, 0.0 ),
	vec3( 0.0331941, 0.9668058, 0.0 ),
	vec3( 0.0170827, 0.0723974, 0.9105199 )
);
const mat3 LINEAR_DISPLAY_P3_TO_LINEAR_SRGB = mat3(
	vec3( 1.2249401, - 0.2249404, 0.0 ),
	vec3( - 0.0420569, 1.0420571, 0.0 ),
	vec3( - 0.0196376, - 0.0786361, 1.0982735 )
);
vec4 LinearSRGBToLinearDisplayP3( in vec4 value ) {
	return vec4( value.rgb * LINEAR_SRGB_TO_LINEAR_DISPLAY_P3, value.a );
}
vec4 LinearDisplayP3ToLinearSRGB( in vec4 value ) {
	return vec4( value.rgb * LINEAR_DISPLAY_P3_TO_LINEAR_SRGB, value.a );
}
vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}
vec4 LinearToLinear( in vec4 value ) {
	return value;
}
vec4 LinearTosRGB( in vec4 value ) {
	return sRGBTransferOETF( value );
}`,e0=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,t0=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,n0=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,i0=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,r0=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,s0=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,o0=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,a0=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,l0=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,c0=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,u0=`#ifdef USE_LIGHTMAP
	vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
	vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
	reflectedLight.indirectDiffuse += lightMapIrradiance;
#endif`,f0=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,h0=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,d0=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,p0=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	#if defined ( LEGACY_LIGHTS )
		if ( cutoffDistance > 0.0 && decayExponent > 0.0 ) {
			return pow( saturate( - lightDistance / cutoffDistance + 1.0 ), decayExponent );
		}
		return 1.0;
	#else
		float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
		if ( cutoffDistance > 0.0 ) {
			distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
		}
		return distanceFalloff;
	#endif
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,m0=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,g0=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,_0=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,v0=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,x0=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,M0=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,S0=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,y0=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,E0=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,T0=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,b0=`#if defined( USE_LOGDEPTHBUF ) && defined( USE_LOGDEPTHBUF_EXT )
	gl_FragDepthEXT = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,A0=`#if defined( USE_LOGDEPTHBUF ) && defined( USE_LOGDEPTHBUF_EXT )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,w0=`#ifdef USE_LOGDEPTHBUF
	#ifdef USE_LOGDEPTHBUF_EXT
		varying float vFragDepth;
		varying float vIsPerspective;
	#else
		uniform float logDepthBufFC;
	#endif
#endif`,R0=`#ifdef USE_LOGDEPTHBUF
	#ifdef USE_LOGDEPTHBUF_EXT
		vFragDepth = 1.0 + gl_Position.w;
		vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
	#else
		if ( isPerspectiveMatrix( projectionMatrix ) ) {
			gl_Position.z = log2( max( EPSILON, gl_Position.w + 1.0 ) ) * logDepthBufFC - 1.0;
			gl_Position.z *= gl_Position.w;
		}
	#endif
#endif`,C0=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,L0=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,P0=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,D0=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,U0=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,I0=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,N0=`#if defined( USE_MORPHCOLORS ) && defined( MORPHTARGETS_TEXTURE )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,F0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
			if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
		}
	#else
		objectNormal += morphNormal0 * morphTargetInfluences[ 0 ];
		objectNormal += morphNormal1 * morphTargetInfluences[ 1 ];
		objectNormal += morphNormal2 * morphTargetInfluences[ 2 ];
		objectNormal += morphNormal3 * morphTargetInfluences[ 3 ];
	#endif
#endif`,O0=`#ifdef USE_MORPHTARGETS
	uniform float morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
		uniform sampler2DArray morphTargetsTexture;
		uniform ivec2 morphTargetsTextureSize;
		vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
			int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
			int y = texelIndex / morphTargetsTextureSize.x;
			int x = texelIndex - y * morphTargetsTextureSize.x;
			ivec3 morphUV = ivec3( x, y, morphTargetIndex );
			return texelFetch( morphTargetsTexture, morphUV, 0 );
		}
	#else
		#ifndef USE_MORPHNORMALS
			uniform float morphTargetInfluences[ 8 ];
		#else
			uniform float morphTargetInfluences[ 4 ];
		#endif
	#endif
#endif`,B0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	#ifdef MORPHTARGETS_TEXTURE
		for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
			if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
		}
	#else
		transformed += morphTarget0 * morphTargetInfluences[ 0 ];
		transformed += morphTarget1 * morphTargetInfluences[ 1 ];
		transformed += morphTarget2 * morphTargetInfluences[ 2 ];
		transformed += morphTarget3 * morphTargetInfluences[ 3 ];
		#ifndef USE_MORPHNORMALS
			transformed += morphTarget4 * morphTargetInfluences[ 4 ];
			transformed += morphTarget5 * morphTargetInfluences[ 5 ];
			transformed += morphTarget6 * morphTargetInfluences[ 6 ];
			transformed += morphTarget7 * morphTargetInfluences[ 7 ];
		#endif
	#endif
#endif`,z0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,k0=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,H0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,G0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,V0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,W0=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,X0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,q0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,Y0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,j0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,$0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,K0=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;
const vec3 PackFactors = vec3( 256. * 256. * 256., 256. * 256., 256. );
const vec4 UnpackFactors = UnpackDownscale / vec4( PackFactors, 1. );
const float ShiftRight8 = 1. / 256.;
vec4 packDepthToRGBA( const in float v ) {
	vec4 r = vec4( fract( v * PackFactors ), v );
	r.yzw -= r.xyz * ShiftRight8;	return r * PackUpscale;
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors );
}
vec2 packDepthToRG( in highp float v ) {
	return packDepthToRGBA( v ).yx;
}
float unpackRGToDepth( const in highp vec2 v ) {
	return unpackRGBAToDepth( vec4( v.xy, 0.0, 0.0 ) );
}
vec4 pack2HalfToRGBA( vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,Z0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,J0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,Q0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,ev=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,tv=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,nv=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,iv=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return shadow;
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
		vec3 lightToPosition = shadowCoord.xyz;
		float dp = ( length( lightToPosition ) - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );		dp += shadowBias;
		vec3 bd3D = normalize( lightToPosition );
		#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
			vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
			return (
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
				texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
			) * ( 1.0 / 9.0 );
		#else
			return texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
		#endif
	}
#endif`,rv=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,sv=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,ov=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,av=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,lv=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,cv=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,uv=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,fv=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,hv=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,dv=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,pv=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 OptimizedCineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color *= toneMappingExposure;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	return color;
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,mv=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,gv=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
		vec3 refractedRayExit = position + transmissionRay;
		vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
		vec2 refractionCoords = ndcPos.xy / ndcPos.w;
		refractionCoords += 1.0;
		refractionCoords /= 2.0;
		vec4 transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
		vec3 transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,_v=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,vv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,xv=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,Mv=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const Sv=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,yv=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ev=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Tv=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,bv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Av=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,wv=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,Rv=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( 1.0 );
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#endif
}`,Cv=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,Lv=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( 1.0 );
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,Pv=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,Dv=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Uv=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,Iv=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Nv=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,Fv=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Ov=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Bv=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,zv=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,kv=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Hv=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,Gv=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), opacity );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,Vv=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Wv=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Xv=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,qv=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Yv=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,jv=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec4 diffuseColor = vec4( diffuse, opacity );
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$v=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Kv=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Zv=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Jv=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,Qv=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );
	vec2 scale;
	scale.x = length( vec3( modelMatrix[ 0 ].x, modelMatrix[ 0 ].y, modelMatrix[ 0 ].z ) );
	scale.y = length( vec3( modelMatrix[ 1 ].x, modelMatrix[ 1 ].y, modelMatrix[ 1 ].z ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,ex=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,it={alphahash_fragment:y_,alphahash_pars_fragment:E_,alphamap_fragment:T_,alphamap_pars_fragment:b_,alphatest_fragment:A_,alphatest_pars_fragment:w_,aomap_fragment:R_,aomap_pars_fragment:C_,batching_pars_vertex:L_,batching_vertex:P_,begin_vertex:D_,beginnormal_vertex:U_,bsdfs:I_,iridescence_fragment:N_,bumpmap_pars_fragment:F_,clipping_planes_fragment:O_,clipping_planes_pars_fragment:B_,clipping_planes_pars_vertex:z_,clipping_planes_vertex:k_,color_fragment:H_,color_pars_fragment:G_,color_pars_vertex:V_,color_vertex:W_,common:X_,cube_uv_reflection_fragment:q_,defaultnormal_vertex:Y_,displacementmap_pars_vertex:j_,displacementmap_vertex:$_,emissivemap_fragment:K_,emissivemap_pars_fragment:Z_,colorspace_fragment:J_,colorspace_pars_fragment:Q_,envmap_fragment:e0,envmap_common_pars_fragment:t0,envmap_pars_fragment:n0,envmap_pars_vertex:i0,envmap_physical_pars_fragment:m0,envmap_vertex:r0,fog_vertex:s0,fog_pars_vertex:o0,fog_fragment:a0,fog_pars_fragment:l0,gradientmap_pars_fragment:c0,lightmap_fragment:u0,lightmap_pars_fragment:f0,lights_lambert_fragment:h0,lights_lambert_pars_fragment:d0,lights_pars_begin:p0,lights_toon_fragment:g0,lights_toon_pars_fragment:_0,lights_phong_fragment:v0,lights_phong_pars_fragment:x0,lights_physical_fragment:M0,lights_physical_pars_fragment:S0,lights_fragment_begin:y0,lights_fragment_maps:E0,lights_fragment_end:T0,logdepthbuf_fragment:b0,logdepthbuf_pars_fragment:A0,logdepthbuf_pars_vertex:w0,logdepthbuf_vertex:R0,map_fragment:C0,map_pars_fragment:L0,map_particle_fragment:P0,map_particle_pars_fragment:D0,metalnessmap_fragment:U0,metalnessmap_pars_fragment:I0,morphcolor_vertex:N0,morphnormal_vertex:F0,morphtarget_pars_vertex:O0,morphtarget_vertex:B0,normal_fragment_begin:z0,normal_fragment_maps:k0,normal_pars_fragment:H0,normal_pars_vertex:G0,normal_vertex:V0,normalmap_pars_fragment:W0,clearcoat_normal_fragment_begin:X0,clearcoat_normal_fragment_maps:q0,clearcoat_pars_fragment:Y0,iridescence_pars_fragment:j0,opaque_fragment:$0,packing:K0,premultiplied_alpha_fragment:Z0,project_vertex:J0,dithering_fragment:Q0,dithering_pars_fragment:ev,roughnessmap_fragment:tv,roughnessmap_pars_fragment:nv,shadowmap_pars_fragment:iv,shadowmap_pars_vertex:rv,shadowmap_vertex:sv,shadowmask_pars_fragment:ov,skinbase_vertex:av,skinning_pars_vertex:lv,skinning_vertex:cv,skinnormal_vertex:uv,specularmap_fragment:fv,specularmap_pars_fragment:hv,tonemapping_fragment:dv,tonemapping_pars_fragment:pv,transmission_fragment:mv,transmission_pars_fragment:gv,uv_pars_fragment:_v,uv_pars_vertex:vv,uv_vertex:xv,worldpos_vertex:Mv,background_vert:Sv,background_frag:yv,backgroundCube_vert:Ev,backgroundCube_frag:Tv,cube_vert:bv,cube_frag:Av,depth_vert:wv,depth_frag:Rv,distanceRGBA_vert:Cv,distanceRGBA_frag:Lv,equirect_vert:Pv,equirect_frag:Dv,linedashed_vert:Uv,linedashed_frag:Iv,meshbasic_vert:Nv,meshbasic_frag:Fv,meshlambert_vert:Ov,meshlambert_frag:Bv,meshmatcap_vert:zv,meshmatcap_frag:kv,meshnormal_vert:Hv,meshnormal_frag:Gv,meshphong_vert:Vv,meshphong_frag:Wv,meshphysical_vert:Xv,meshphysical_frag:qv,meshtoon_vert:Yv,meshtoon_frag:jv,points_vert:$v,points_frag:Kv,shadow_vert:Zv,shadow_frag:Jv,sprite_vert:Qv,sprite_frag:ex},Ee={common:{diffuse:{value:new ft(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new at}},envmap:{envMap:{value:null},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new at}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new at}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new at},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new at},normalScale:{value:new qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new at},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new at}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new at}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new at}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new ft(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new ft(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0},uvTransform:{value:new at}},sprite:{diffuse:{value:new ft(16777215)},opacity:{value:1},center:{value:new qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new at},alphaMap:{value:null},alphaMapTransform:{value:new at},alphaTest:{value:0}}},vi={basic:{uniforms:Mn([Ee.common,Ee.specularmap,Ee.envmap,Ee.aomap,Ee.lightmap,Ee.fog]),vertexShader:it.meshbasic_vert,fragmentShader:it.meshbasic_frag},lambert:{uniforms:Mn([Ee.common,Ee.specularmap,Ee.envmap,Ee.aomap,Ee.lightmap,Ee.emissivemap,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,Ee.fog,Ee.lights,{emissive:{value:new ft(0)}}]),vertexShader:it.meshlambert_vert,fragmentShader:it.meshlambert_frag},phong:{uniforms:Mn([Ee.common,Ee.specularmap,Ee.envmap,Ee.aomap,Ee.lightmap,Ee.emissivemap,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,Ee.fog,Ee.lights,{emissive:{value:new ft(0)},specular:{value:new ft(1118481)},shininess:{value:30}}]),vertexShader:it.meshphong_vert,fragmentShader:it.meshphong_frag},standard:{uniforms:Mn([Ee.common,Ee.envmap,Ee.aomap,Ee.lightmap,Ee.emissivemap,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,Ee.roughnessmap,Ee.metalnessmap,Ee.fog,Ee.lights,{emissive:{value:new ft(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag},toon:{uniforms:Mn([Ee.common,Ee.aomap,Ee.lightmap,Ee.emissivemap,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,Ee.gradientmap,Ee.fog,Ee.lights,{emissive:{value:new ft(0)}}]),vertexShader:it.meshtoon_vert,fragmentShader:it.meshtoon_frag},matcap:{uniforms:Mn([Ee.common,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,Ee.fog,{matcap:{value:null}}]),vertexShader:it.meshmatcap_vert,fragmentShader:it.meshmatcap_frag},points:{uniforms:Mn([Ee.points,Ee.fog]),vertexShader:it.points_vert,fragmentShader:it.points_frag},dashed:{uniforms:Mn([Ee.common,Ee.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:it.linedashed_vert,fragmentShader:it.linedashed_frag},depth:{uniforms:Mn([Ee.common,Ee.displacementmap]),vertexShader:it.depth_vert,fragmentShader:it.depth_frag},normal:{uniforms:Mn([Ee.common,Ee.bumpmap,Ee.normalmap,Ee.displacementmap,{opacity:{value:1}}]),vertexShader:it.meshnormal_vert,fragmentShader:it.meshnormal_frag},sprite:{uniforms:Mn([Ee.sprite,Ee.fog]),vertexShader:it.sprite_vert,fragmentShader:it.sprite_frag},background:{uniforms:{uvTransform:{value:new at},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:it.background_vert,fragmentShader:it.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1}},vertexShader:it.backgroundCube_vert,fragmentShader:it.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:it.cube_vert,fragmentShader:it.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:it.equirect_vert,fragmentShader:it.equirect_frag},distanceRGBA:{uniforms:Mn([Ee.common,Ee.displacementmap,{referencePosition:{value:new k},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:it.distanceRGBA_vert,fragmentShader:it.distanceRGBA_frag},shadow:{uniforms:Mn([Ee.lights,Ee.fog,{color:{value:new ft(0)},opacity:{value:1}}]),vertexShader:it.shadow_vert,fragmentShader:it.shadow_frag}};vi.physical={uniforms:Mn([vi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new at},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new at},clearcoatNormalScale:{value:new qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new at},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new at},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new at},sheen:{value:0},sheenColor:{value:new ft(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new at},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new at},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new at},transmissionSamplerSize:{value:new qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new at},attenuationDistance:{value:0},attenuationColor:{value:new ft(0)},specularColor:{value:new ft(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new at},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new at},anisotropyVector:{value:new qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new at}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag};const Ea={r:0,b:0,g:0};function tx(i,e,t,n,r,s,o){const a=new ft(0);let l=s===!0?0:1,c,u,f=null,d=0,m=null;function v(p,h){let x=!1,_=h.isScene===!0?h.background:null;_&&_.isTexture&&(_=(h.backgroundBlurriness>0?t:e).get(_)),_===null?M(a,l):_&&_.isColor&&(M(_,1),x=!0);const y=i.xr.getEnvironmentBlendMode();y==="additive"?n.buffers.color.setClear(0,0,0,1,o):y==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||x)&&i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil),_&&(_.isCubeTexture||_.mapping===al)?(u===void 0&&(u=new Mi(new Xo(1,1,1),new qr({name:"BackgroundCubeMaterial",uniforms:Vs(vi.backgroundCube.uniforms),vertexShader:vi.backgroundCube.vertexShader,fragmentShader:vi.backgroundCube.fragmentShader,side:Ln,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(D,b,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),r.update(u)),u.material.uniforms.envMap.value=_,u.material.uniforms.flipEnvMap.value=_.isCubeTexture&&_.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=h.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=h.backgroundIntensity,u.material.toneMapped=Tt.getTransfer(_.colorSpace)!==It,(f!==_||d!==_.version||m!==i.toneMapping)&&(u.material.needsUpdate=!0,f=_,d=_.version,m=i.toneMapping),u.layers.enableAll(),p.unshift(u,u.geometry,u.material,0,0,null)):_&&_.isTexture&&(c===void 0&&(c=new Mi(new yu(2,2),new qr({name:"BackgroundMaterial",uniforms:Vs(vi.background.uniforms),vertexShader:vi.background.vertexShader,fragmentShader:vi.background.fragmentShader,side:gr,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),r.update(c)),c.material.uniforms.t2D.value=_,c.material.uniforms.backgroundIntensity.value=h.backgroundIntensity,c.material.toneMapped=Tt.getTransfer(_.colorSpace)!==It,_.matrixAutoUpdate===!0&&_.updateMatrix(),c.material.uniforms.uvTransform.value.copy(_.matrix),(f!==_||d!==_.version||m!==i.toneMapping)&&(c.material.needsUpdate=!0,f=_,d=_.version,m=i.toneMapping),c.layers.enableAll(),p.unshift(c,c.geometry,c.material,0,0,null))}function M(p,h){p.getRGB(Ea,gp(i)),n.buffers.color.setClear(Ea.r,Ea.g,Ea.b,h,o)}return{getClearColor:function(){return a},setClearColor:function(p,h=1){a.set(p),l=h,M(a,l)},getClearAlpha:function(){return l},setClearAlpha:function(p){l=p,M(a,l)},render:v}}function nx(i,e,t,n){const r=i.getParameter(i.MAX_VERTEX_ATTRIBS),s=n.isWebGL2?null:e.get("OES_vertex_array_object"),o=n.isWebGL2||s!==null,a={},l=p(null);let c=l,u=!1;function f(N,B,V,W,ie){let te=!1;if(o){const Q=M(W,V,B);c!==Q&&(c=Q,m(c.object)),te=h(N,W,V,ie),te&&x(N,W,V,ie)}else{const Q=B.wireframe===!0;(c.geometry!==W.id||c.program!==V.id||c.wireframe!==Q)&&(c.geometry=W.id,c.program=V.id,c.wireframe=Q,te=!0)}ie!==null&&t.update(ie,i.ELEMENT_ARRAY_BUFFER),(te||u)&&(u=!1,q(N,B,V,W),ie!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,t.get(ie).buffer))}function d(){return n.isWebGL2?i.createVertexArray():s.createVertexArrayOES()}function m(N){return n.isWebGL2?i.bindVertexArray(N):s.bindVertexArrayOES(N)}function v(N){return n.isWebGL2?i.deleteVertexArray(N):s.deleteVertexArrayOES(N)}function M(N,B,V){const W=V.wireframe===!0;let ie=a[N.id];ie===void 0&&(ie={},a[N.id]=ie);let te=ie[B.id];te===void 0&&(te={},ie[B.id]=te);let Q=te[W];return Q===void 0&&(Q=p(d()),te[W]=Q),Q}function p(N){const B=[],V=[],W=[];for(let ie=0;ie<r;ie++)B[ie]=0,V[ie]=0,W[ie]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:B,enabledAttributes:V,attributeDivisors:W,object:N,attributes:{},index:null}}function h(N,B,V,W){const ie=c.attributes,te=B.attributes;let Q=0;const ae=V.getAttributes();for(const re in ae)if(ae[re].location>=0){const se=ie[re];let ve=te[re];if(ve===void 0&&(re==="instanceMatrix"&&N.instanceMatrix&&(ve=N.instanceMatrix),re==="instanceColor"&&N.instanceColor&&(ve=N.instanceColor)),se===void 0||se.attribute!==ve||ve&&se.data!==ve.data)return!0;Q++}return c.attributesNum!==Q||c.index!==W}function x(N,B,V,W){const ie={},te=B.attributes;let Q=0;const ae=V.getAttributes();for(const re in ae)if(ae[re].location>=0){let se=te[re];se===void 0&&(re==="instanceMatrix"&&N.instanceMatrix&&(se=N.instanceMatrix),re==="instanceColor"&&N.instanceColor&&(se=N.instanceColor));const ve={};ve.attribute=se,se&&se.data&&(ve.data=se.data),ie[re]=ve,Q++}c.attributes=ie,c.attributesNum=Q,c.index=W}function _(){const N=c.newAttributes;for(let B=0,V=N.length;B<V;B++)N[B]=0}function y(N){D(N,0)}function D(N,B){const V=c.newAttributes,W=c.enabledAttributes,ie=c.attributeDivisors;V[N]=1,W[N]===0&&(i.enableVertexAttribArray(N),W[N]=1),ie[N]!==B&&((n.isWebGL2?i:e.get("ANGLE_instanced_arrays"))[n.isWebGL2?"vertexAttribDivisor":"vertexAttribDivisorANGLE"](N,B),ie[N]=B)}function b(){const N=c.newAttributes,B=c.enabledAttributes;for(let V=0,W=B.length;V<W;V++)B[V]!==N[V]&&(i.disableVertexAttribArray(V),B[V]=0)}function R(N,B,V,W,ie,te,Q){Q===!0?i.vertexAttribIPointer(N,B,V,ie,te):i.vertexAttribPointer(N,B,V,W,ie,te)}function q(N,B,V,W){if(n.isWebGL2===!1&&(N.isInstancedMesh||W.isInstancedBufferGeometry)&&e.get("ANGLE_instanced_arrays")===null)return;_();const ie=W.attributes,te=V.getAttributes(),Q=B.defaultAttributeValues;for(const ae in te){const re=te[ae];if(re.location>=0){let z=ie[ae];if(z===void 0&&(ae==="instanceMatrix"&&N.instanceMatrix&&(z=N.instanceMatrix),ae==="instanceColor"&&N.instanceColor&&(z=N.instanceColor)),z!==void 0){const se=z.normalized,ve=z.itemSize,Se=t.get(z);if(Se===void 0)continue;const ge=Se.buffer,ke=Se.type,Be=Se.bytesPerElement,be=n.isWebGL2===!0&&(ke===i.INT||ke===i.UNSIGNED_INT||z.gpuType===ep);if(z.isInterleavedBufferAttribute){const Ke=z.data,j=Ke.stride,xt=z.offset;if(Ke.isInstancedInterleavedBuffer){for(let Ue=0;Ue<re.locationSize;Ue++)D(re.location+Ue,Ke.meshPerAttribute);N.isInstancedMesh!==!0&&W._maxInstanceCount===void 0&&(W._maxInstanceCount=Ke.meshPerAttribute*Ke.count)}else for(let Ue=0;Ue<re.locationSize;Ue++)y(re.location+Ue);i.bindBuffer(i.ARRAY_BUFFER,ge);for(let Ue=0;Ue<re.locationSize;Ue++)R(re.location+Ue,ve/re.locationSize,ke,se,j*Be,(xt+ve/re.locationSize*Ue)*Be,be)}else{if(z.isInstancedBufferAttribute){for(let Ke=0;Ke<re.locationSize;Ke++)D(re.location+Ke,z.meshPerAttribute);N.isInstancedMesh!==!0&&W._maxInstanceCount===void 0&&(W._maxInstanceCount=z.meshPerAttribute*z.count)}else for(let Ke=0;Ke<re.locationSize;Ke++)y(re.location+Ke);i.bindBuffer(i.ARRAY_BUFFER,ge);for(let Ke=0;Ke<re.locationSize;Ke++)R(re.location+Ke,ve/re.locationSize,ke,se,ve*Be,ve/re.locationSize*Ke*Be,be)}}else if(Q!==void 0){const se=Q[ae];if(se!==void 0)switch(se.length){case 2:i.vertexAttrib2fv(re.location,se);break;case 3:i.vertexAttrib3fv(re.location,se);break;case 4:i.vertexAttrib4fv(re.location,se);break;default:i.vertexAttrib1fv(re.location,se)}}}}b()}function T(){Y();for(const N in a){const B=a[N];for(const V in B){const W=B[V];for(const ie in W)v(W[ie].object),delete W[ie];delete B[V]}delete a[N]}}function A(N){if(a[N.id]===void 0)return;const B=a[N.id];for(const V in B){const W=B[V];for(const ie in W)v(W[ie].object),delete W[ie];delete B[V]}delete a[N.id]}function I(N){for(const B in a){const V=a[B];if(V[N.id]===void 0)continue;const W=V[N.id];for(const ie in W)v(W[ie].object),delete W[ie];delete V[N.id]}}function Y(){J(),u=!0,c!==l&&(c=l,m(c.object))}function J(){l.geometry=null,l.program=null,l.wireframe=!1}return{setup:f,reset:Y,resetDefaultState:J,dispose:T,releaseStatesOfGeometry:A,releaseStatesOfProgram:I,initAttributes:_,enableAttribute:y,disableUnusedAttributes:b}}function ix(i,e,t,n){const r=n.isWebGL2;let s;function o(u){s=u}function a(u,f){i.drawArrays(s,u,f),t.update(f,s,1)}function l(u,f,d){if(d===0)return;let m,v;if(r)m=i,v="drawArraysInstanced";else if(m=e.get("ANGLE_instanced_arrays"),v="drawArraysInstancedANGLE",m===null){console.error("THREE.WebGLBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.");return}m[v](s,u,f,d),t.update(f,s,d)}function c(u,f,d){if(d===0)return;const m=e.get("WEBGL_multi_draw");if(m===null)for(let v=0;v<d;v++)this.render(u[v],f[v]);else{m.multiDrawArraysWEBGL(s,u,0,f,0,d);let v=0;for(let M=0;M<d;M++)v+=f[M];t.update(v,s,1)}}this.setMode=o,this.render=a,this.renderInstances=l,this.renderMultiDraw=c}function rx(i,e,t){let n;function r(){if(n!==void 0)return n;if(e.has("EXT_texture_filter_anisotropic")===!0){const R=e.get("EXT_texture_filter_anisotropic");n=i.getParameter(R.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else n=0;return n}function s(R){if(R==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";R="mediump"}return R==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}const o=typeof WebGL2RenderingContext<"u"&&i.constructor.name==="WebGL2RenderingContext";let a=t.precision!==void 0?t.precision:"highp";const l=s(a);l!==a&&(console.warn("THREE.WebGLRenderer:",a,"not supported, using",l,"instead."),a=l);const c=o||e.has("WEBGL_draw_buffers"),u=t.logarithmicDepthBuffer===!0,f=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),d=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_TEXTURE_SIZE),v=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),M=i.getParameter(i.MAX_VERTEX_ATTRIBS),p=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),h=i.getParameter(i.MAX_VARYING_VECTORS),x=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),_=d>0,y=o||e.has("OES_texture_float"),D=_&&y,b=o?i.getParameter(i.MAX_SAMPLES):0;return{isWebGL2:o,drawBuffers:c,getMaxAnisotropy:r,getMaxPrecision:s,precision:a,logarithmicDepthBuffer:u,maxTextures:f,maxVertexTextures:d,maxTextureSize:m,maxCubemapSize:v,maxAttributes:M,maxVertexUniforms:p,maxVaryings:h,maxFragmentUniforms:x,vertexTextures:_,floatFragmentTextures:y,floatVertexTextures:D,maxSamples:b}}function sx(i){const e=this;let t=null,n=0,r=!1,s=!1;const o=new ir,a=new at,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(f,d){const m=f.length!==0||d||n!==0||r;return r=d,n=f.length,m},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(f,d){t=u(f,d,0)},this.setState=function(f,d,m){const v=f.clippingPlanes,M=f.clipIntersection,p=f.clipShadows,h=i.get(f);if(!r||v===null||v.length===0||s&&!p)s?u(null):c();else{const x=s?0:n,_=x*4;let y=h.clippingState||null;l.value=y,y=u(v,d,_,m);for(let D=0;D!==_;++D)y[D]=t[D];h.clippingState=y,this.numIntersection=M?this.numPlanes:0,this.numPlanes+=x}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(f,d,m,v){const M=f!==null?f.length:0;let p=null;if(M!==0){if(p=l.value,v!==!0||p===null){const h=m+M*4,x=d.matrixWorldInverse;a.getNormalMatrix(x),(p===null||p.length<h)&&(p=new Float32Array(h));for(let _=0,y=m;_!==M;++_,y+=4)o.copy(f[_]).applyMatrix4(x,a),o.normal.toArray(p,y),p[y+3]=o.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=M,e.numIntersection=0,p}}function ox(i){let e=new WeakMap;function t(o,a){return a===$c?o.mapping=ks:a===Kc&&(o.mapping=Hs),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===$c||a===Kc)if(e.has(o)){const l=e.get(o).texture;return t(l,o.mapping)}else{const l=o.image;if(l&&l.height>0){const c=new v_(l.height/2);return c.fromEquirectangularTexture(i,o),e.set(o,c),o.addEventListener("dispose",r),t(c.texture,o.mapping)}else return null}}return o}function r(o){const a=o.target;a.removeEventListener("dispose",r);const l=e.get(a);l!==void 0&&(e.delete(a),l.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class Mp extends _p{constructor(e=-1,t=1,n=1,r=-1,s=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=r,this.near=s,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,r,s,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=r,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,r=(this.top+this.bottom)/2;let s=n-e,o=n+e,a=r+t,l=r-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,o=s+c*this.view.width,a-=u*this.view.offsetY,l=a-u*this.view.height}this.projectionMatrix.makeOrthographic(s,o,a,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ds=4,mh=[.125,.215,.35,.446,.526,.582],Or=20,oc=new Mp,gh=new ft;let ac=null,lc=0,cc=0;const Ur=(1+Math.sqrt(5))/2,bs=1/Ur,_h=[new k(1,1,1),new k(-1,1,1),new k(1,1,-1),new k(-1,1,-1),new k(0,Ur,bs),new k(0,Ur,-bs),new k(bs,0,Ur),new k(-bs,0,Ur),new k(Ur,bs,0),new k(-Ur,bs,0)];class vh{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,r=100){ac=this._renderer.getRenderTarget(),lc=this._renderer.getActiveCubeFace(),cc=this._renderer.getActiveMipmapLevel(),this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,r,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Sh(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Mh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ac,lc,cc),e.scissorTest=!1,Ta(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===ks||e.mapping===Hs?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ac=this._renderer.getRenderTarget(),lc=this._renderer.getActiveCubeFace(),cc=this._renderer.getActiveMipmapLevel();const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Kn,minFilter:Kn,generateMipmaps:!1,type:Fo,format:fi,colorSpace:Wi,depthBuffer:!1},r=xh(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=xh(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=ax(s)),this._blurMaterial=lx(s,e,t)}return r}_compileMaterial(e){const t=new Mi(this._lodPlanes[0],e);this._renderer.compile(t,oc)}_sceneToCubeUV(e,t,n,r){const a=new Jn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,f=u.autoClear,d=u.toneMapping;u.getClearColor(gh),u.toneMapping=lr,u.autoClear=!1;const m=new ul({name:"PMREM.Background",side:Ln,depthWrite:!1,depthTest:!1}),v=new Mi(new Xo,m);let M=!1;const p=e.background;p?p.isColor&&(m.color.copy(p),e.background=null,M=!0):(m.color.copy(gh),M=!0);for(let h=0;h<6;h++){const x=h%3;x===0?(a.up.set(0,l[h],0),a.lookAt(c[h],0,0)):x===1?(a.up.set(0,0,l[h]),a.lookAt(0,c[h],0)):(a.up.set(0,l[h],0),a.lookAt(0,0,c[h]));const _=this._cubeSize;Ta(r,x*_,h>2?_:0,_,_),u.setRenderTarget(r),M&&u.render(v,a),u.render(e,a)}v.geometry.dispose(),v.material.dispose(),u.toneMapping=d,u.autoClear=f,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,r=e.mapping===ks||e.mapping===Hs;r?(this._cubemapMaterial===null&&(this._cubemapMaterial=Sh()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Mh());const s=r?this._cubemapMaterial:this._equirectMaterial,o=new Mi(this._lodPlanes[0],s),a=s.uniforms;a.envMap.value=e;const l=this._cubeSize;Ta(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(o,oc)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;for(let r=1;r<this._lodPlanes.length;r++){const s=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),o=_h[(r-1)%_h.length];this._blur(e,r-1,r,s,o)}t.autoClear=n}_blur(e,t,n,r,s){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,r,"latitudinal",s),this._halfBlur(o,e,n,n,r,"longitudinal",s)}_halfBlur(e,t,n,r,s,o,a){const l=this._renderer,c=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,f=new Mi(this._lodPlanes[r],c),d=c.uniforms,m=this._sizeLods[n]-1,v=isFinite(s)?Math.PI/(2*m):2*Math.PI/(2*Or-1),M=s/v,p=isFinite(s)?1+Math.floor(u*M):Or;p>Or&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Or}`);const h=[];let x=0;for(let R=0;R<Or;++R){const q=R/M,T=Math.exp(-q*q/2);h.push(T),R===0?x+=T:R<p&&(x+=2*T)}for(let R=0;R<h.length;R++)h[R]=h[R]/x;d.envMap.value=e.texture,d.samples.value=p,d.weights.value=h,d.latitudinal.value=o==="latitudinal",a&&(d.poleAxis.value=a);const{_lodMax:_}=this;d.dTheta.value=v,d.mipInt.value=_-n;const y=this._sizeLods[r],D=3*y*(r>_-Ds?r-_+Ds:0),b=4*(this._cubeSize-y);Ta(t,D,b,3*y,2*y),l.setRenderTarget(t),l.render(f,oc)}}function ax(i){const e=[],t=[],n=[];let r=i;const s=i-Ds+1+mh.length;for(let o=0;o<s;o++){const a=Math.pow(2,r);t.push(a);let l=1/a;o>i-Ds?l=mh[o-i+Ds-1]:o===0&&(l=0),n.push(l);const c=1/(a-2),u=-c,f=1+c,d=[u,u,f,u,f,f,u,u,f,f,u,f],m=6,v=6,M=3,p=2,h=1,x=new Float32Array(M*v*m),_=new Float32Array(p*v*m),y=new Float32Array(h*v*m);for(let b=0;b<m;b++){const R=b%3*2/3-1,q=b>2?0:-1,T=[R,q,0,R+2/3,q,0,R+2/3,q+1,0,R,q,0,R+2/3,q+1,0,R,q+1,0];x.set(T,M*v*b),_.set(d,p*v*b);const A=[b,b,b,b,b,b];y.set(A,h*v*b)}const D=new An;D.setAttribute("position",new Gn(x,M)),D.setAttribute("uv",new Gn(_,p)),D.setAttribute("faceIndex",new Gn(y,h)),e.push(D),r>Ds&&r--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function xh(i,e,t){const n=new Xr(i,e,t);return n.texture.mapping=al,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Ta(i,e,t,n,r){i.viewport.set(e,t,n,r),i.scissor.set(e,t,n,r)}function lx(i,e,t){const n=new Float32Array(Or),r=new k(0,1,0);return new qr({name:"SphericalGaussianBlur",defines:{n:Or,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:r}},vertexShader:Eu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:ar,depthTest:!1,depthWrite:!1})}function Mh(){return new qr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Eu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:ar,depthTest:!1,depthWrite:!1})}function Sh(){return new qr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Eu(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ar,depthTest:!1,depthWrite:!1})}function Eu(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function cx(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const l=a.mapping,c=l===$c||l===Kc,u=l===ks||l===Hs;if(c||u)if(a.isRenderTargetTexture&&a.needsPMREMUpdate===!0){a.needsPMREMUpdate=!1;let f=e.get(a);return t===null&&(t=new vh(i)),f=c?t.fromEquirectangular(a,f):t.fromCubemap(a,f),e.set(a,f),f.texture}else{if(e.has(a))return e.get(a).texture;{const f=a.image;if(c&&f&&f.height>0||u&&f&&r(f)){t===null&&(t=new vh(i));const d=c?t.fromEquirectangular(a):t.fromCubemap(a);return e.set(a,d),a.addEventListener("dispose",s),d.texture}else return null}}}return a}function r(a){let l=0;const c=6;for(let u=0;u<c;u++)a[u]!==void 0&&l++;return l===c}function s(a){const l=a.target;l.removeEventListener("dispose",s);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function ux(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let r;switch(n){case"WEBGL_depth_texture":r=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":r=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":r=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":r=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:r=i.getExtension(n)}return e[n]=r,r}return{has:function(n){return t(n)!==null},init:function(n){n.isWebGL2?(t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance")):(t("WEBGL_depth_texture"),t("OES_texture_float"),t("OES_texture_half_float"),t("OES_texture_half_float_linear"),t("OES_standard_derivatives"),t("OES_element_index_uint"),t("OES_vertex_array_object"),t("ANGLE_instanced_arrays")),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture")},get:function(n){const r=t(n);return r===null&&console.warn("THREE.WebGLRenderer: "+n+" extension not supported."),r}}}function fx(i,e,t,n){const r={},s=new WeakMap;function o(f){const d=f.target;d.index!==null&&e.remove(d.index);for(const v in d.attributes)e.remove(d.attributes[v]);for(const v in d.morphAttributes){const M=d.morphAttributes[v];for(let p=0,h=M.length;p<h;p++)e.remove(M[p])}d.removeEventListener("dispose",o),delete r[d.id];const m=s.get(d);m&&(e.remove(m),s.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function a(f,d){return r[d.id]===!0||(d.addEventListener("dispose",o),r[d.id]=!0,t.memory.geometries++),d}function l(f){const d=f.attributes;for(const v in d)e.update(d[v],i.ARRAY_BUFFER);const m=f.morphAttributes;for(const v in m){const M=m[v];for(let p=0,h=M.length;p<h;p++)e.update(M[p],i.ARRAY_BUFFER)}}function c(f){const d=[],m=f.index,v=f.attributes.position;let M=0;if(m!==null){const x=m.array;M=m.version;for(let _=0,y=x.length;_<y;_+=3){const D=x[_+0],b=x[_+1],R=x[_+2];d.push(D,b,b,R,R,D)}}else if(v!==void 0){const x=v.array;M=v.version;for(let _=0,y=x.length/3-1;_<y;_+=3){const D=_+0,b=_+1,R=_+2;d.push(D,b,b,R,R,D)}}else return;const p=new(cp(d)?mp:pp)(d,1);p.version=M;const h=s.get(f);h&&e.remove(h),s.set(f,p)}function u(f){const d=s.get(f);if(d){const m=f.index;m!==null&&d.version<m.version&&c(f)}else c(f);return s.get(f)}return{get:a,update:l,getWireframeAttribute:u}}function hx(i,e,t,n){const r=n.isWebGL2;let s;function o(m){s=m}let a,l;function c(m){a=m.type,l=m.bytesPerElement}function u(m,v){i.drawElements(s,v,a,m*l),t.update(v,s,1)}function f(m,v,M){if(M===0)return;let p,h;if(r)p=i,h="drawElementsInstanced";else if(p=e.get("ANGLE_instanced_arrays"),h="drawElementsInstancedANGLE",p===null){console.error("THREE.WebGLIndexedBufferRenderer: using THREE.InstancedBufferGeometry but hardware does not support extension ANGLE_instanced_arrays.");return}p[h](s,v,a,m*l,M),t.update(v,s,M)}function d(m,v,M){if(M===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let h=0;h<M;h++)this.render(m[h]/l,v[h]);else{p.multiDrawElementsWEBGL(s,v,0,a,m,0,M);let h=0;for(let x=0;x<M;x++)h+=v[x];t.update(h,s,1)}}this.setMode=o,this.setIndex=c,this.render=u,this.renderInstances=f,this.renderMultiDraw=d}function dx(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(s/3);break;case i.LINES:t.lines+=a*(s/2);break;case i.LINE_STRIP:t.lines+=a*(s-1);break;case i.LINE_LOOP:t.lines+=a*s;break;case i.POINTS:t.points+=a*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function r(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:r,update:n}}function px(i,e){return i[0]-e[0]}function mx(i,e){return Math.abs(e[1])-Math.abs(i[1])}function gx(i,e,t){const n={},r=new Float32Array(8),s=new WeakMap,o=new an,a=[];for(let c=0;c<8;c++)a[c]=[c,0];function l(c,u,f){const d=c.morphTargetInfluences;if(e.isWebGL2===!0){const v=u.morphAttributes.position||u.morphAttributes.normal||u.morphAttributes.color,M=v!==void 0?v.length:0;let p=s.get(u);if(p===void 0||p.count!==M){let B=function(){J.dispose(),s.delete(u),u.removeEventListener("dispose",B)};var m=B;p!==void 0&&p.texture.dispose();const _=u.morphAttributes.position!==void 0,y=u.morphAttributes.normal!==void 0,D=u.morphAttributes.color!==void 0,b=u.morphAttributes.position||[],R=u.morphAttributes.normal||[],q=u.morphAttributes.color||[];let T=0;_===!0&&(T=1),y===!0&&(T=2),D===!0&&(T=3);let A=u.attributes.position.count*T,I=1;A>e.maxTextureSize&&(I=Math.ceil(A/e.maxTextureSize),A=e.maxTextureSize);const Y=new Float32Array(A*I*4*M),J=new hp(Y,A,I,M);J.type=or,J.needsUpdate=!0;const N=T*4;for(let V=0;V<M;V++){const W=b[V],ie=R[V],te=q[V],Q=A*I*4*V;for(let ae=0;ae<W.count;ae++){const re=ae*N;_===!0&&(o.fromBufferAttribute(W,ae),Y[Q+re+0]=o.x,Y[Q+re+1]=o.y,Y[Q+re+2]=o.z,Y[Q+re+3]=0),y===!0&&(o.fromBufferAttribute(ie,ae),Y[Q+re+4]=o.x,Y[Q+re+5]=o.y,Y[Q+re+6]=o.z,Y[Q+re+7]=0),D===!0&&(o.fromBufferAttribute(te,ae),Y[Q+re+8]=o.x,Y[Q+re+9]=o.y,Y[Q+re+10]=o.z,Y[Q+re+11]=te.itemSize===4?o.w:1)}}p={count:M,texture:J,size:new qe(A,I)},s.set(u,p),u.addEventListener("dispose",B)}let h=0;for(let _=0;_<d.length;_++)h+=d[_];const x=u.morphTargetsRelative?1:1-h;f.getUniforms().setValue(i,"morphTargetBaseInfluence",x),f.getUniforms().setValue(i,"morphTargetInfluences",d),f.getUniforms().setValue(i,"morphTargetsTexture",p.texture,t),f.getUniforms().setValue(i,"morphTargetsTextureSize",p.size)}else{const v=d===void 0?0:d.length;let M=n[u.id];if(M===void 0||M.length!==v){M=[];for(let y=0;y<v;y++)M[y]=[y,0];n[u.id]=M}for(let y=0;y<v;y++){const D=M[y];D[0]=y,D[1]=d[y]}M.sort(mx);for(let y=0;y<8;y++)y<v&&M[y][1]?(a[y][0]=M[y][0],a[y][1]=M[y][1]):(a[y][0]=Number.MAX_SAFE_INTEGER,a[y][1]=0);a.sort(px);const p=u.morphAttributes.position,h=u.morphAttributes.normal;let x=0;for(let y=0;y<8;y++){const D=a[y],b=D[0],R=D[1];b!==Number.MAX_SAFE_INTEGER&&R?(p&&u.getAttribute("morphTarget"+y)!==p[b]&&u.setAttribute("morphTarget"+y,p[b]),h&&u.getAttribute("morphNormal"+y)!==h[b]&&u.setAttribute("morphNormal"+y,h[b]),r[y]=R,x+=R):(p&&u.hasAttribute("morphTarget"+y)===!0&&u.deleteAttribute("morphTarget"+y),h&&u.hasAttribute("morphNormal"+y)===!0&&u.deleteAttribute("morphNormal"+y),r[y]=0)}const _=u.morphTargetsRelative?1:1-x;f.getUniforms().setValue(i,"morphTargetBaseInfluence",_),f.getUniforms().setValue(i,"morphTargetInfluences",r)}}return{update:l}}function _x(i,e,t,n){let r=new WeakMap;function s(l){const c=n.render.frame,u=l.geometry,f=e.get(l,u);if(r.get(f)!==c&&(e.update(f),r.set(f,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",a)===!1&&l.addEventListener("dispose",a),r.get(l)!==c&&(t.update(l.instanceMatrix,i.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,i.ARRAY_BUFFER),r.set(l,c))),l.isSkinnedMesh){const d=l.skeleton;r.get(d)!==c&&(d.update(),r.set(d,c))}return f}function o(){r=new WeakMap}function a(l){const c=l.target;c.removeEventListener("dispose",a),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:s,dispose:o}}class Sp extends Pn{constructor(e,t,n,r,s,o,a,l,c,u){if(u=u!==void 0?u:Hr,u!==Hr&&u!==Gs)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===Hr&&(n=sr),n===void 0&&u===Gs&&(n=kr),super(null,r,s,o,a,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:Sn,this.minFilter=l!==void 0?l:Sn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const yp=new Pn,Ep=new Sp(1,1);Ep.compareFunction=lp;const Tp=new hp,bp=new t_,Ap=new vp,yh=[],Eh=[],Th=new Float32Array(16),bh=new Float32Array(9),Ah=new Float32Array(4);function Zs(i,e,t){const n=i[0];if(n<=0||n>0)return i;const r=e*t;let s=yh[r];if(s===void 0&&(s=new Float32Array(r),yh[r]=s),e!==0){n.toArray(s,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(s,a)}return s}function Jt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function Qt(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function fl(i,e){let t=Eh[e];t===void 0&&(t=new Int32Array(e),Eh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function vx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function xx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2fv(this.addr,e),Qt(t,e)}}function Mx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Jt(t,e))return;i.uniform3fv(this.addr,e),Qt(t,e)}}function Sx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4fv(this.addr,e),Qt(t,e)}}function yx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;Ah.set(n),i.uniformMatrix2fv(this.addr,!1,Ah),Qt(t,n)}}function Ex(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;bh.set(n),i.uniformMatrix3fv(this.addr,!1,bh),Qt(t,n)}}function Tx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Jt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),Qt(t,e)}else{if(Jt(t,n))return;Th.set(n),i.uniformMatrix4fv(this.addr,!1,Th),Qt(t,n)}}function bx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function Ax(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2iv(this.addr,e),Qt(t,e)}}function wx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Jt(t,e))return;i.uniform3iv(this.addr,e),Qt(t,e)}}function Rx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4iv(this.addr,e),Qt(t,e)}}function Cx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function Lx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Jt(t,e))return;i.uniform2uiv(this.addr,e),Qt(t,e)}}function Px(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Jt(t,e))return;i.uniform3uiv(this.addr,e),Qt(t,e)}}function Dx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Jt(t,e))return;i.uniform4uiv(this.addr,e),Qt(t,e)}}function Ux(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r);const s=this.type===i.SAMPLER_2D_SHADOW?Ep:yp;t.setTexture2D(e||s,r)}function Ix(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture3D(e||bp,r)}function Nx(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTextureCube(e||Ap,r)}function Fx(i,e,t){const n=this.cache,r=t.allocateTextureUnit();n[0]!==r&&(i.uniform1i(this.addr,r),n[0]=r),t.setTexture2DArray(e||Tp,r)}function Ox(i){switch(i){case 5126:return vx;case 35664:return xx;case 35665:return Mx;case 35666:return Sx;case 35674:return yx;case 35675:return Ex;case 35676:return Tx;case 5124:case 35670:return bx;case 35667:case 35671:return Ax;case 35668:case 35672:return wx;case 35669:case 35673:return Rx;case 5125:return Cx;case 36294:return Lx;case 36295:return Px;case 36296:return Dx;case 35678:case 36198:case 36298:case 36306:case 35682:return Ux;case 35679:case 36299:case 36307:return Ix;case 35680:case 36300:case 36308:case 36293:return Nx;case 36289:case 36303:case 36311:case 36292:return Fx}}function Bx(i,e){i.uniform1fv(this.addr,e)}function zx(i,e){const t=Zs(e,this.size,2);i.uniform2fv(this.addr,t)}function kx(i,e){const t=Zs(e,this.size,3);i.uniform3fv(this.addr,t)}function Hx(i,e){const t=Zs(e,this.size,4);i.uniform4fv(this.addr,t)}function Gx(i,e){const t=Zs(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Vx(i,e){const t=Zs(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Wx(i,e){const t=Zs(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Xx(i,e){i.uniform1iv(this.addr,e)}function qx(i,e){i.uniform2iv(this.addr,e)}function Yx(i,e){i.uniform3iv(this.addr,e)}function jx(i,e){i.uniform4iv(this.addr,e)}function $x(i,e){i.uniform1uiv(this.addr,e)}function Kx(i,e){i.uniform2uiv(this.addr,e)}function Zx(i,e){i.uniform3uiv(this.addr,e)}function Jx(i,e){i.uniform4uiv(this.addr,e)}function Qx(i,e,t){const n=this.cache,r=e.length,s=fl(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let o=0;o!==r;++o)t.setTexture2D(e[o]||yp,s[o])}function eM(i,e,t){const n=this.cache,r=e.length,s=fl(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let o=0;o!==r;++o)t.setTexture3D(e[o]||bp,s[o])}function tM(i,e,t){const n=this.cache,r=e.length,s=fl(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let o=0;o!==r;++o)t.setTextureCube(e[o]||Ap,s[o])}function nM(i,e,t){const n=this.cache,r=e.length,s=fl(t,r);Jt(n,s)||(i.uniform1iv(this.addr,s),Qt(n,s));for(let o=0;o!==r;++o)t.setTexture2DArray(e[o]||Tp,s[o])}function iM(i){switch(i){case 5126:return Bx;case 35664:return zx;case 35665:return kx;case 35666:return Hx;case 35674:return Gx;case 35675:return Vx;case 35676:return Wx;case 5124:case 35670:return Xx;case 35667:case 35671:return qx;case 35668:case 35672:return Yx;case 35669:case 35673:return jx;case 5125:return $x;case 36294:return Kx;case 36295:return Zx;case 36296:return Jx;case 35678:case 36198:case 36298:case 36306:case 35682:return Qx;case 35679:case 36299:case 36307:return eM;case 35680:case 36300:case 36308:case 36293:return tM;case 36289:case 36303:case 36311:case 36292:return nM}}class rM{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Ox(t.type)}}class sM{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=iM(t.type)}}class oM{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const r=this.seq;for(let s=0,o=r.length;s!==o;++s){const a=r[s];a.setValue(e,t[a.id],n)}}}const uc=/(\w+)(\])?(\[|\.)?/g;function wh(i,e){i.seq.push(e),i.map[e.id]=e}function aM(i,e,t){const n=i.name,r=n.length;for(uc.lastIndex=0;;){const s=uc.exec(n),o=uc.lastIndex;let a=s[1];const l=s[2]==="]",c=s[3];if(l&&(a=a|0),c===void 0||c==="["&&o+2===r){wh(t,c===void 0?new rM(a,i,e):new sM(a,i,e));break}else{let f=t.map[a];f===void 0&&(f=new oM(a),wh(t,f)),t=f}}}class Va{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let r=0;r<n;++r){const s=e.getActiveUniform(t,r),o=e.getUniformLocation(t,s.name);aM(s,o,this)}}setValue(e,t,n,r){const s=this.map[t];s!==void 0&&s.setValue(e,n,r)}setOptional(e,t,n){const r=t[n];r!==void 0&&this.setValue(e,n,r)}static upload(e,t,n,r){for(let s=0,o=t.length;s!==o;++s){const a=t[s],l=n[a.id];l.needsUpdate!==!1&&a.setValue(e,l.value,r)}}static seqWithValue(e,t){const n=[];for(let r=0,s=e.length;r!==s;++r){const o=e[r];o.id in t&&n.push(o)}return n}}function Rh(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const lM=37297;let cM=0;function uM(i,e){const t=i.split(`
`),n=[],r=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let o=r;o<s;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}function fM(i){const e=Tt.getPrimaries(Tt.workingColorSpace),t=Tt.getPrimaries(i);let n;switch(e===t?n="":e===$a&&t===ja?n="LinearDisplayP3ToLinearSRGB":e===ja&&t===$a&&(n="LinearSRGBToLinearDisplayP3"),i){case Wi:case ll:return[n,"LinearTransferOETF"];case fn:case xu:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",i),[n,"LinearTransferOETF"]}}function Ch(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),r=i.getShaderInfoLog(e).trim();if(n&&r==="")return"";const s=/ERROR: 0:(\d+)/.exec(r);if(s){const o=parseInt(s[1]);return t.toUpperCase()+`

`+r+`

`+uM(i.getShaderSource(e),o)}else return r}function hM(i,e){const t=fM(e);return`vec4 ${i}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function dM(i,e){let t;switch(e){case yg:t="Linear";break;case Eg:t="Reinhard";break;case Tg:t="OptimizedCineon";break;case bg:t="ACESFilmic";break;case wg:t="AgX";break;case Ag:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}function pM(i){return[i.extensionDerivatives||i.envMapCubeUVHeight||i.bumpMap||i.normalMapTangentSpace||i.clearcoatNormalMap||i.flatShading||i.shaderID==="physical"?"#extension GL_OES_standard_derivatives : enable":"",(i.extensionFragDepth||i.logarithmicDepthBuffer)&&i.rendererExtensionFragDepth?"#extension GL_EXT_frag_depth : enable":"",i.extensionDrawBuffers&&i.rendererExtensionDrawBuffers?"#extension GL_EXT_draw_buffers : require":"",(i.extensionShaderTextureLOD||i.envMap||i.transmission)&&i.rendererExtensionShaderTextureLod?"#extension GL_EXT_shader_texture_lod : enable":""].filter(Us).join(`
`)}function mM(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":""].filter(Us).join(`
`)}function gM(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function _M(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let r=0;r<n;r++){const s=i.getActiveAttrib(e,r),o=s.name;let a=1;s.type===i.FLOAT_MAT2&&(a=2),s.type===i.FLOAT_MAT3&&(a=3),s.type===i.FLOAT_MAT4&&(a=4),t[o]={type:s.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function Us(i){return i!==""}function Lh(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Ph(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const vM=/^[ \t]*#include +<([\w\d./]+)>/gm;function iu(i){return i.replace(vM,MM)}const xM=new Map([["encodings_fragment","colorspace_fragment"],["encodings_pars_fragment","colorspace_pars_fragment"],["output_fragment","opaque_fragment"]]);function MM(i,e){let t=it[e];if(t===void 0){const n=xM.get(e);if(n!==void 0)t=it[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return iu(t)}const SM=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Dh(i){return i.replace(SM,yM)}function yM(i,e,t,n){let r="";for(let s=parseInt(e);s<parseInt(t);s++)r+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return r}function Uh(i){let e="precision "+i.precision+` float;
precision `+i.precision+" int;";return i.precision==="highp"?e+=`
#define HIGH_PRECISION`:i.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:i.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function EM(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Zd?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Km?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ii&&(e="SHADOWMAP_TYPE_VSM"),e}function TM(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case ks:case Hs:e="ENVMAP_TYPE_CUBE";break;case al:e="ENVMAP_TYPE_CUBE_UV";break}return e}function bM(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Hs:e="ENVMAP_MODE_REFRACTION";break}return e}function AM(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Jd:e="ENVMAP_BLENDING_MULTIPLY";break;case Mg:e="ENVMAP_BLENDING_MIX";break;case Sg:e="ENVMAP_BLENDING_ADD";break}return e}function wM(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function RM(i,e,t,n){const r=i.getContext(),s=t.defines;let o=t.vertexShader,a=t.fragmentShader;const l=EM(t),c=TM(t),u=bM(t),f=AM(t),d=wM(t),m=t.isWebGL2?"":pM(t),v=mM(t),M=gM(s),p=r.createProgram();let h,x,_=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(h=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,M].filter(Us).join(`
`),h.length>0&&(h+=`
`),x=[m,"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,M].filter(Us).join(`
`),x.length>0&&(x+=`
`)):(h=[Uh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,M,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors&&t.isWebGL2?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_TEXTURE":"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0&&t.isWebGL2?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.useLegacyLights?"#define LEGACY_LIGHTS":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.logarithmicDepthBuffer&&t.rendererExtensionFragDepth?"#define USE_LOGDEPTHBUF_EXT":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#if ( defined( USE_MORPHTARGETS ) && ! defined( MORPHTARGETS_TEXTURE ) )","	attribute vec3 morphTarget0;","	attribute vec3 morphTarget1;","	attribute vec3 morphTarget2;","	attribute vec3 morphTarget3;","	#ifdef USE_MORPHNORMALS","		attribute vec3 morphNormal0;","		attribute vec3 morphNormal1;","		attribute vec3 morphNormal2;","		attribute vec3 morphNormal3;","	#else","		attribute vec3 morphTarget4;","		attribute vec3 morphTarget5;","		attribute vec3 morphTarget6;","		attribute vec3 morphTarget7;","	#endif","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Us).join(`
`),x=[m,Uh(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,M,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+f:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.useLegacyLights?"#define LEGACY_LIGHTS":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.logarithmicDepthBuffer&&t.rendererExtensionFragDepth?"#define USE_LOGDEPTHBUF_EXT":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==lr?"#define TONE_MAPPING":"",t.toneMapping!==lr?it.tonemapping_pars_fragment:"",t.toneMapping!==lr?dM("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",it.colorspace_pars_fragment,hM("linearToOutputTexel",t.outputColorSpace),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Us).join(`
`)),o=iu(o),o=Lh(o,t),o=Ph(o,t),a=iu(a),a=Lh(a,t),a=Ph(a,t),o=Dh(o),a=Dh(a),t.isWebGL2&&t.isRawShaderMaterial!==!0&&(_=`#version 300 es
`,h=[v,"precision mediump sampler2DArray;","#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+h,x=["precision mediump sampler2DArray;","#define varying in",t.glslVersion===Zf?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Zf?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+x);const y=_+h+o,D=_+x+a,b=Rh(r,r.VERTEX_SHADER,y),R=Rh(r,r.FRAGMENT_SHADER,D);r.attachShader(p,b),r.attachShader(p,R),t.index0AttributeName!==void 0?r.bindAttribLocation(p,0,t.index0AttributeName):t.morphTargets===!0&&r.bindAttribLocation(p,0,"position"),r.linkProgram(p);function q(Y){if(i.debug.checkShaderErrors){const J=r.getProgramInfoLog(p).trim(),N=r.getShaderInfoLog(b).trim(),B=r.getShaderInfoLog(R).trim();let V=!0,W=!0;if(r.getProgramParameter(p,r.LINK_STATUS)===!1)if(V=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(r,p,b,R);else{const ie=Ch(r,b,"vertex"),te=Ch(r,R,"fragment");console.error("THREE.WebGLProgram: Shader Error "+r.getError()+" - VALIDATE_STATUS "+r.getProgramParameter(p,r.VALIDATE_STATUS)+`

Program Info Log: `+J+`
`+ie+`
`+te)}else J!==""?console.warn("THREE.WebGLProgram: Program Info Log:",J):(N===""||B==="")&&(W=!1);W&&(Y.diagnostics={runnable:V,programLog:J,vertexShader:{log:N,prefix:h},fragmentShader:{log:B,prefix:x}})}r.deleteShader(b),r.deleteShader(R),T=new Va(r,p),A=_M(r,p)}let T;this.getUniforms=function(){return T===void 0&&q(this),T};let A;this.getAttributes=function(){return A===void 0&&q(this),A};let I=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return I===!1&&(I=r.getProgramParameter(p,lM)),I},this.destroy=function(){n.releaseStatesOfProgram(this),r.deleteProgram(p),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=cM++,this.cacheKey=e,this.usedTimes=1,this.program=p,this.vertexShader=b,this.fragmentShader=R,this}let CM=0;class LM{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,r=this._getShaderStage(t),s=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(r)===!1&&(o.add(r),r.usedTimes++),o.has(s)===!1&&(o.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new PM(e),t.set(e,n)),n}}class PM{constructor(e){this.id=CM++,this.code=e,this.usedTimes=0}}function DM(i,e,t,n,r,s,o){const a=new Mu,l=new LM,c=[],u=r.isWebGL2,f=r.logarithmicDepthBuffer,d=r.vertexTextures;let m=r.precision;const v={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function M(T){return T===0?"uv":`uv${T}`}function p(T,A,I,Y,J){const N=Y.fog,B=J.geometry,V=T.isMeshStandardMaterial?Y.environment:null,W=(T.isMeshStandardMaterial?t:e).get(T.envMap||V),ie=W&&W.mapping===al?W.image.height:null,te=v[T.type];T.precision!==null&&(m=r.getMaxPrecision(T.precision),m!==T.precision&&console.warn("THREE.WebGLProgram.getParameters:",T.precision,"not supported, using",m,"instead."));const Q=B.morphAttributes.position||B.morphAttributes.normal||B.morphAttributes.color,ae=Q!==void 0?Q.length:0;let re=0;B.morphAttributes.position!==void 0&&(re=1),B.morphAttributes.normal!==void 0&&(re=2),B.morphAttributes.color!==void 0&&(re=3);let z,se,ve,Se;if(te){const St=vi[te];z=St.vertexShader,se=St.fragmentShader}else z=T.vertexShader,se=T.fragmentShader,l.update(T),ve=l.getVertexShaderID(T),Se=l.getFragmentShaderID(T);const ge=i.getRenderTarget(),ke=J.isInstancedMesh===!0,Be=J.isBatchedMesh===!0,be=!!T.map,Ke=!!T.matcap,j=!!W,xt=!!T.aoMap,Ue=!!T.lightMap,Ve=!!T.bumpMap,Le=!!T.normalMap,mt=!!T.displacementMap,Ze=!!T.emissiveMap,L=!!T.metalnessMap,E=!!T.roughnessMap,$=T.anisotropy>0,ue=T.clearcoat>0,ce=T.iridescence>0,ee=T.sheen>0,ne=T.transmission>0,fe=$&&!!T.anisotropyMap,Me=ue&&!!T.clearcoatMap,Fe=ue&&!!T.clearcoatNormalMap,Ye=ue&&!!T.clearcoatRoughnessMap,le=ce&&!!T.iridescenceMap,rt=ce&&!!T.iridescenceThicknessMap,Ge=ee&&!!T.sheenColorMap,Oe=ee&&!!T.sheenRoughnessMap,Ce=!!T.specularMap,ye=!!T.specularColorMap,U=!!T.specularIntensityMap,pe=ne&&!!T.transmissionMap,De=ne&&!!T.thicknessMap,Ae=!!T.gradientMap,he=!!T.alphaMap,F=T.alphaTest>0,me=!!T.alphaHash,Te=!!T.extensions,Xe=!!B.attributes.uv1,He=!!B.attributes.uv2,st=!!B.attributes.uv3;let ot=lr;return T.toneMapped&&(ge===null||ge.isXRRenderTarget===!0)&&(ot=i.toneMapping),{isWebGL2:u,shaderID:te,shaderType:T.type,shaderName:T.name,vertexShader:z,fragmentShader:se,defines:T.defines,customVertexShaderID:ve,customFragmentShaderID:Se,isRawShaderMaterial:T.isRawShaderMaterial===!0,glslVersion:T.glslVersion,precision:m,batching:Be,instancing:ke,instancingColor:ke&&J.instanceColor!==null,supportsVertexTextures:d,outputColorSpace:ge===null?i.outputColorSpace:ge.isXRRenderTarget===!0?ge.texture.colorSpace:Wi,map:be,matcap:Ke,envMap:j,envMapMode:j&&W.mapping,envMapCubeUVHeight:ie,aoMap:xt,lightMap:Ue,bumpMap:Ve,normalMap:Le,displacementMap:d&&mt,emissiveMap:Ze,normalMapObjectSpace:Le&&T.normalMapType===kg,normalMapTangentSpace:Le&&T.normalMapType===zg,metalnessMap:L,roughnessMap:E,anisotropy:$,anisotropyMap:fe,clearcoat:ue,clearcoatMap:Me,clearcoatNormalMap:Fe,clearcoatRoughnessMap:Ye,iridescence:ce,iridescenceMap:le,iridescenceThicknessMap:rt,sheen:ee,sheenColorMap:Ge,sheenRoughnessMap:Oe,specularMap:Ce,specularColorMap:ye,specularIntensityMap:U,transmission:ne,transmissionMap:pe,thicknessMap:De,gradientMap:Ae,opaque:T.transparent===!1&&T.blending===Fs,alphaMap:he,alphaTest:F,alphaHash:me,combine:T.combine,mapUv:be&&M(T.map.channel),aoMapUv:xt&&M(T.aoMap.channel),lightMapUv:Ue&&M(T.lightMap.channel),bumpMapUv:Ve&&M(T.bumpMap.channel),normalMapUv:Le&&M(T.normalMap.channel),displacementMapUv:mt&&M(T.displacementMap.channel),emissiveMapUv:Ze&&M(T.emissiveMap.channel),metalnessMapUv:L&&M(T.metalnessMap.channel),roughnessMapUv:E&&M(T.roughnessMap.channel),anisotropyMapUv:fe&&M(T.anisotropyMap.channel),clearcoatMapUv:Me&&M(T.clearcoatMap.channel),clearcoatNormalMapUv:Fe&&M(T.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:Ye&&M(T.clearcoatRoughnessMap.channel),iridescenceMapUv:le&&M(T.iridescenceMap.channel),iridescenceThicknessMapUv:rt&&M(T.iridescenceThicknessMap.channel),sheenColorMapUv:Ge&&M(T.sheenColorMap.channel),sheenRoughnessMapUv:Oe&&M(T.sheenRoughnessMap.channel),specularMapUv:Ce&&M(T.specularMap.channel),specularColorMapUv:ye&&M(T.specularColorMap.channel),specularIntensityMapUv:U&&M(T.specularIntensityMap.channel),transmissionMapUv:pe&&M(T.transmissionMap.channel),thicknessMapUv:De&&M(T.thicknessMap.channel),alphaMapUv:he&&M(T.alphaMap.channel),vertexTangents:!!B.attributes.tangent&&(Le||$),vertexColors:T.vertexColors,vertexAlphas:T.vertexColors===!0&&!!B.attributes.color&&B.attributes.color.itemSize===4,vertexUv1s:Xe,vertexUv2s:He,vertexUv3s:st,pointsUvs:J.isPoints===!0&&!!B.attributes.uv&&(be||he),fog:!!N,useFog:T.fog===!0,fogExp2:N&&N.isFogExp2,flatShading:T.flatShading===!0,sizeAttenuation:T.sizeAttenuation===!0,logarithmicDepthBuffer:f,skinning:J.isSkinnedMesh===!0,morphTargets:B.morphAttributes.position!==void 0,morphNormals:B.morphAttributes.normal!==void 0,morphColors:B.morphAttributes.color!==void 0,morphTargetsCount:ae,morphTextureStride:re,numDirLights:A.directional.length,numPointLights:A.point.length,numSpotLights:A.spot.length,numSpotLightMaps:A.spotLightMap.length,numRectAreaLights:A.rectArea.length,numHemiLights:A.hemi.length,numDirLightShadows:A.directionalShadowMap.length,numPointLightShadows:A.pointShadowMap.length,numSpotLightShadows:A.spotShadowMap.length,numSpotLightShadowsWithMaps:A.numSpotLightShadowsWithMaps,numLightProbes:A.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:T.dithering,shadowMapEnabled:i.shadowMap.enabled&&I.length>0,shadowMapType:i.shadowMap.type,toneMapping:ot,useLegacyLights:i._useLegacyLights,decodeVideoTexture:be&&T.map.isVideoTexture===!0&&Tt.getTransfer(T.map.colorSpace)===It,premultipliedAlpha:T.premultipliedAlpha,doubleSided:T.side===xi,flipSided:T.side===Ln,useDepthPacking:T.depthPacking>=0,depthPacking:T.depthPacking||0,index0AttributeName:T.index0AttributeName,extensionDerivatives:Te&&T.extensions.derivatives===!0,extensionFragDepth:Te&&T.extensions.fragDepth===!0,extensionDrawBuffers:Te&&T.extensions.drawBuffers===!0,extensionShaderTextureLOD:Te&&T.extensions.shaderTextureLOD===!0,extensionClipCullDistance:Te&&T.extensions.clipCullDistance&&n.has("WEBGL_clip_cull_distance"),rendererExtensionFragDepth:u||n.has("EXT_frag_depth"),rendererExtensionDrawBuffers:u||n.has("WEBGL_draw_buffers"),rendererExtensionShaderTextureLod:u||n.has("EXT_shader_texture_lod"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:T.customProgramCacheKey()}}function h(T){const A=[];if(T.shaderID?A.push(T.shaderID):(A.push(T.customVertexShaderID),A.push(T.customFragmentShaderID)),T.defines!==void 0)for(const I in T.defines)A.push(I),A.push(T.defines[I]);return T.isRawShaderMaterial===!1&&(x(A,T),_(A,T),A.push(i.outputColorSpace)),A.push(T.customProgramCacheKey),A.join()}function x(T,A){T.push(A.precision),T.push(A.outputColorSpace),T.push(A.envMapMode),T.push(A.envMapCubeUVHeight),T.push(A.mapUv),T.push(A.alphaMapUv),T.push(A.lightMapUv),T.push(A.aoMapUv),T.push(A.bumpMapUv),T.push(A.normalMapUv),T.push(A.displacementMapUv),T.push(A.emissiveMapUv),T.push(A.metalnessMapUv),T.push(A.roughnessMapUv),T.push(A.anisotropyMapUv),T.push(A.clearcoatMapUv),T.push(A.clearcoatNormalMapUv),T.push(A.clearcoatRoughnessMapUv),T.push(A.iridescenceMapUv),T.push(A.iridescenceThicknessMapUv),T.push(A.sheenColorMapUv),T.push(A.sheenRoughnessMapUv),T.push(A.specularMapUv),T.push(A.specularColorMapUv),T.push(A.specularIntensityMapUv),T.push(A.transmissionMapUv),T.push(A.thicknessMapUv),T.push(A.combine),T.push(A.fogExp2),T.push(A.sizeAttenuation),T.push(A.morphTargetsCount),T.push(A.morphAttributeCount),T.push(A.numDirLights),T.push(A.numPointLights),T.push(A.numSpotLights),T.push(A.numSpotLightMaps),T.push(A.numHemiLights),T.push(A.numRectAreaLights),T.push(A.numDirLightShadows),T.push(A.numPointLightShadows),T.push(A.numSpotLightShadows),T.push(A.numSpotLightShadowsWithMaps),T.push(A.numLightProbes),T.push(A.shadowMapType),T.push(A.toneMapping),T.push(A.numClippingPlanes),T.push(A.numClipIntersection),T.push(A.depthPacking)}function _(T,A){a.disableAll(),A.isWebGL2&&a.enable(0),A.supportsVertexTextures&&a.enable(1),A.instancing&&a.enable(2),A.instancingColor&&a.enable(3),A.matcap&&a.enable(4),A.envMap&&a.enable(5),A.normalMapObjectSpace&&a.enable(6),A.normalMapTangentSpace&&a.enable(7),A.clearcoat&&a.enable(8),A.iridescence&&a.enable(9),A.alphaTest&&a.enable(10),A.vertexColors&&a.enable(11),A.vertexAlphas&&a.enable(12),A.vertexUv1s&&a.enable(13),A.vertexUv2s&&a.enable(14),A.vertexUv3s&&a.enable(15),A.vertexTangents&&a.enable(16),A.anisotropy&&a.enable(17),A.alphaHash&&a.enable(18),A.batching&&a.enable(19),T.push(a.mask),a.disableAll(),A.fog&&a.enable(0),A.useFog&&a.enable(1),A.flatShading&&a.enable(2),A.logarithmicDepthBuffer&&a.enable(3),A.skinning&&a.enable(4),A.morphTargets&&a.enable(5),A.morphNormals&&a.enable(6),A.morphColors&&a.enable(7),A.premultipliedAlpha&&a.enable(8),A.shadowMapEnabled&&a.enable(9),A.useLegacyLights&&a.enable(10),A.doubleSided&&a.enable(11),A.flipSided&&a.enable(12),A.useDepthPacking&&a.enable(13),A.dithering&&a.enable(14),A.transmission&&a.enable(15),A.sheen&&a.enable(16),A.opaque&&a.enable(17),A.pointsUvs&&a.enable(18),A.decodeVideoTexture&&a.enable(19),T.push(a.mask)}function y(T){const A=v[T.type];let I;if(A){const Y=vi[A];I=p_.clone(Y.uniforms)}else I=T.uniforms;return I}function D(T,A){let I;for(let Y=0,J=c.length;Y<J;Y++){const N=c[Y];if(N.cacheKey===A){I=N,++I.usedTimes;break}}return I===void 0&&(I=new RM(i,A,T,s),c.push(I)),I}function b(T){if(--T.usedTimes===0){const A=c.indexOf(T);c[A]=c[c.length-1],c.pop(),T.destroy()}}function R(T){l.remove(T)}function q(){l.dispose()}return{getParameters:p,getProgramCacheKey:h,getUniforms:y,acquireProgram:D,releaseProgram:b,releaseShaderCache:R,programs:c,dispose:q}}function UM(){let i=new WeakMap;function e(s){let o=i.get(s);return o===void 0&&(o={},i.set(s,o)),o}function t(s){i.delete(s)}function n(s,o,a){i.get(s)[o]=a}function r(){i=new WeakMap}return{get:e,remove:t,update:n,dispose:r}}function IM(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Ih(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function Nh(){const i=[];let e=0;const t=[],n=[],r=[];function s(){e=0,t.length=0,n.length=0,r.length=0}function o(f,d,m,v,M,p){let h=i[e];return h===void 0?(h={id:f.id,object:f,geometry:d,material:m,groupOrder:v,renderOrder:f.renderOrder,z:M,group:p},i[e]=h):(h.id=f.id,h.object=f,h.geometry=d,h.material=m,h.groupOrder=v,h.renderOrder=f.renderOrder,h.z=M,h.group=p),e++,h}function a(f,d,m,v,M,p){const h=o(f,d,m,v,M,p);m.transmission>0?n.push(h):m.transparent===!0?r.push(h):t.push(h)}function l(f,d,m,v,M,p){const h=o(f,d,m,v,M,p);m.transmission>0?n.unshift(h):m.transparent===!0?r.unshift(h):t.unshift(h)}function c(f,d){t.length>1&&t.sort(f||IM),n.length>1&&n.sort(d||Ih),r.length>1&&r.sort(d||Ih)}function u(){for(let f=e,d=i.length;f<d;f++){const m=i[f];if(m.id===null)break;m.id=null,m.object=null,m.geometry=null,m.material=null,m.group=null}}return{opaque:t,transmissive:n,transparent:r,init:s,push:a,unshift:l,finish:u,sort:c}}function NM(){let i=new WeakMap;function e(n,r){const s=i.get(n);let o;return s===void 0?(o=new Nh,i.set(n,[o])):r>=s.length?(o=new Nh,s.push(o)):o=s[r],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function FM(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new k,color:new ft};break;case"SpotLight":t={position:new k,direction:new k,color:new ft,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new k,color:new ft,distance:0,decay:0};break;case"HemisphereLight":t={direction:new k,skyColor:new ft,groundColor:new ft};break;case"RectAreaLight":t={color:new ft,position:new k,halfWidth:new k,halfHeight:new k};break}return i[e.id]=t,t}}}function OM(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"SpotLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe};break;case"PointLight":t={shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let BM=0;function zM(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function kM(i,e){const t=new FM,n=OM(),r={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let u=0;u<9;u++)r.probe.push(new k);const s=new k,o=new Bt,a=new Bt;function l(u,f){let d=0,m=0,v=0;for(let Y=0;Y<9;Y++)r.probe[Y].set(0,0,0);let M=0,p=0,h=0,x=0,_=0,y=0,D=0,b=0,R=0,q=0,T=0;u.sort(zM);const A=f===!0?Math.PI:1;for(let Y=0,J=u.length;Y<J;Y++){const N=u[Y],B=N.color,V=N.intensity,W=N.distance,ie=N.shadow&&N.shadow.map?N.shadow.map.texture:null;if(N.isAmbientLight)d+=B.r*V*A,m+=B.g*V*A,v+=B.b*V*A;else if(N.isLightProbe){for(let te=0;te<9;te++)r.probe[te].addScaledVector(N.sh.coefficients[te],V);T++}else if(N.isDirectionalLight){const te=t.get(N);if(te.color.copy(N.color).multiplyScalar(N.intensity*A),N.castShadow){const Q=N.shadow,ae=n.get(N);ae.shadowBias=Q.bias,ae.shadowNormalBias=Q.normalBias,ae.shadowRadius=Q.radius,ae.shadowMapSize=Q.mapSize,r.directionalShadow[M]=ae,r.directionalShadowMap[M]=ie,r.directionalShadowMatrix[M]=N.shadow.matrix,y++}r.directional[M]=te,M++}else if(N.isSpotLight){const te=t.get(N);te.position.setFromMatrixPosition(N.matrixWorld),te.color.copy(B).multiplyScalar(V*A),te.distance=W,te.coneCos=Math.cos(N.angle),te.penumbraCos=Math.cos(N.angle*(1-N.penumbra)),te.decay=N.decay,r.spot[h]=te;const Q=N.shadow;if(N.map&&(r.spotLightMap[R]=N.map,R++,Q.updateMatrices(N),N.castShadow&&q++),r.spotLightMatrix[h]=Q.matrix,N.castShadow){const ae=n.get(N);ae.shadowBias=Q.bias,ae.shadowNormalBias=Q.normalBias,ae.shadowRadius=Q.radius,ae.shadowMapSize=Q.mapSize,r.spotShadow[h]=ae,r.spotShadowMap[h]=ie,b++}h++}else if(N.isRectAreaLight){const te=t.get(N);te.color.copy(B).multiplyScalar(V),te.halfWidth.set(N.width*.5,0,0),te.halfHeight.set(0,N.height*.5,0),r.rectArea[x]=te,x++}else if(N.isPointLight){const te=t.get(N);if(te.color.copy(N.color).multiplyScalar(N.intensity*A),te.distance=N.distance,te.decay=N.decay,N.castShadow){const Q=N.shadow,ae=n.get(N);ae.shadowBias=Q.bias,ae.shadowNormalBias=Q.normalBias,ae.shadowRadius=Q.radius,ae.shadowMapSize=Q.mapSize,ae.shadowCameraNear=Q.camera.near,ae.shadowCameraFar=Q.camera.far,r.pointShadow[p]=ae,r.pointShadowMap[p]=ie,r.pointShadowMatrix[p]=N.shadow.matrix,D++}r.point[p]=te,p++}else if(N.isHemisphereLight){const te=t.get(N);te.skyColor.copy(N.color).multiplyScalar(V*A),te.groundColor.copy(N.groundColor).multiplyScalar(V*A),r.hemi[_]=te,_++}}x>0&&(e.isWebGL2?i.has("OES_texture_float_linear")===!0?(r.rectAreaLTC1=Ee.LTC_FLOAT_1,r.rectAreaLTC2=Ee.LTC_FLOAT_2):(r.rectAreaLTC1=Ee.LTC_HALF_1,r.rectAreaLTC2=Ee.LTC_HALF_2):i.has("OES_texture_float_linear")===!0?(r.rectAreaLTC1=Ee.LTC_FLOAT_1,r.rectAreaLTC2=Ee.LTC_FLOAT_2):i.has("OES_texture_half_float_linear")===!0?(r.rectAreaLTC1=Ee.LTC_HALF_1,r.rectAreaLTC2=Ee.LTC_HALF_2):console.error("THREE.WebGLRenderer: Unable to use RectAreaLight. Missing WebGL extensions.")),r.ambient[0]=d,r.ambient[1]=m,r.ambient[2]=v;const I=r.hash;(I.directionalLength!==M||I.pointLength!==p||I.spotLength!==h||I.rectAreaLength!==x||I.hemiLength!==_||I.numDirectionalShadows!==y||I.numPointShadows!==D||I.numSpotShadows!==b||I.numSpotMaps!==R||I.numLightProbes!==T)&&(r.directional.length=M,r.spot.length=h,r.rectArea.length=x,r.point.length=p,r.hemi.length=_,r.directionalShadow.length=y,r.directionalShadowMap.length=y,r.pointShadow.length=D,r.pointShadowMap.length=D,r.spotShadow.length=b,r.spotShadowMap.length=b,r.directionalShadowMatrix.length=y,r.pointShadowMatrix.length=D,r.spotLightMatrix.length=b+R-q,r.spotLightMap.length=R,r.numSpotLightShadowsWithMaps=q,r.numLightProbes=T,I.directionalLength=M,I.pointLength=p,I.spotLength=h,I.rectAreaLength=x,I.hemiLength=_,I.numDirectionalShadows=y,I.numPointShadows=D,I.numSpotShadows=b,I.numSpotMaps=R,I.numLightProbes=T,r.version=BM++)}function c(u,f){let d=0,m=0,v=0,M=0,p=0;const h=f.matrixWorldInverse;for(let x=0,_=u.length;x<_;x++){const y=u[x];if(y.isDirectionalLight){const D=r.directional[d];D.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),D.direction.sub(s),D.direction.transformDirection(h),d++}else if(y.isSpotLight){const D=r.spot[v];D.position.setFromMatrixPosition(y.matrixWorld),D.position.applyMatrix4(h),D.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),D.direction.sub(s),D.direction.transformDirection(h),v++}else if(y.isRectAreaLight){const D=r.rectArea[M];D.position.setFromMatrixPosition(y.matrixWorld),D.position.applyMatrix4(h),a.identity(),o.copy(y.matrixWorld),o.premultiply(h),a.extractRotation(o),D.halfWidth.set(y.width*.5,0,0),D.halfHeight.set(0,y.height*.5,0),D.halfWidth.applyMatrix4(a),D.halfHeight.applyMatrix4(a),M++}else if(y.isPointLight){const D=r.point[m];D.position.setFromMatrixPosition(y.matrixWorld),D.position.applyMatrix4(h),m++}else if(y.isHemisphereLight){const D=r.hemi[p];D.direction.setFromMatrixPosition(y.matrixWorld),D.direction.transformDirection(h),p++}}}return{setup:l,setupView:c,state:r}}function Fh(i,e){const t=new kM(i,e),n=[],r=[];function s(){n.length=0,r.length=0}function o(f){n.push(f)}function a(f){r.push(f)}function l(f){t.setup(n,f)}function c(f){t.setupView(n,f)}return{init:s,state:{lightsArray:n,shadowsArray:r,lights:t},setupLights:l,setupLightsView:c,pushLight:o,pushShadow:a}}function HM(i,e){let t=new WeakMap;function n(s,o=0){const a=t.get(s);let l;return a===void 0?(l=new Fh(i,e),t.set(s,[l])):o>=a.length?(l=new Fh(i,e),a.push(l)):l=a[o],l}function r(){t=new WeakMap}return{get:n,dispose:r}}class GM extends $r{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=Og,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class VM extends $r{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const WM=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,XM=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function qM(i,e,t){let n=new Su;const r=new qe,s=new qe,o=new an,a=new GM({depthPacking:Bg}),l=new VM,c={},u=t.maxTextureSize,f={[gr]:Ln,[Ln]:gr,[xi]:xi},d=new qr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new qe},radius:{value:4}},vertexShader:WM,fragmentShader:XM}),m=d.clone();m.defines.HORIZONTAL_PASS=1;const v=new An;v.setAttribute("position",new Gn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const M=new Mi(v,d),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Zd;let h=this.type;this.render=function(b,R,q){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||b.length===0)return;const T=i.getRenderTarget(),A=i.getActiveCubeFace(),I=i.getActiveMipmapLevel(),Y=i.state;Y.setBlending(ar),Y.buffers.color.setClear(1,1,1,1),Y.buffers.depth.setTest(!0),Y.setScissorTest(!1);const J=h!==Ii&&this.type===Ii,N=h===Ii&&this.type!==Ii;for(let B=0,V=b.length;B<V;B++){const W=b[B],ie=W.shadow;if(ie===void 0){console.warn("THREE.WebGLShadowMap:",W,"has no shadow.");continue}if(ie.autoUpdate===!1&&ie.needsUpdate===!1)continue;r.copy(ie.mapSize);const te=ie.getFrameExtents();if(r.multiply(te),s.copy(ie.mapSize),(r.x>u||r.y>u)&&(r.x>u&&(s.x=Math.floor(u/te.x),r.x=s.x*te.x,ie.mapSize.x=s.x),r.y>u&&(s.y=Math.floor(u/te.y),r.y=s.y*te.y,ie.mapSize.y=s.y)),ie.map===null||J===!0||N===!0){const ae=this.type!==Ii?{minFilter:Sn,magFilter:Sn}:{};ie.map!==null&&ie.map.dispose(),ie.map=new Xr(r.x,r.y,ae),ie.map.texture.name=W.name+".shadowMap",ie.camera.updateProjectionMatrix()}i.setRenderTarget(ie.map),i.clear();const Q=ie.getViewportCount();for(let ae=0;ae<Q;ae++){const re=ie.getViewport(ae);o.set(s.x*re.x,s.y*re.y,s.x*re.z,s.y*re.w),Y.viewport(o),ie.updateMatrices(W,ae),n=ie.getFrustum(),y(R,q,ie.camera,W,this.type)}ie.isPointLightShadow!==!0&&this.type===Ii&&x(ie,q),ie.needsUpdate=!1}h=this.type,p.needsUpdate=!1,i.setRenderTarget(T,A,I)};function x(b,R){const q=e.update(M);d.defines.VSM_SAMPLES!==b.blurSamples&&(d.defines.VSM_SAMPLES=b.blurSamples,m.defines.VSM_SAMPLES=b.blurSamples,d.needsUpdate=!0,m.needsUpdate=!0),b.mapPass===null&&(b.mapPass=new Xr(r.x,r.y)),d.uniforms.shadow_pass.value=b.map.texture,d.uniforms.resolution.value=b.mapSize,d.uniforms.radius.value=b.radius,i.setRenderTarget(b.mapPass),i.clear(),i.renderBufferDirect(R,null,q,d,M,null),m.uniforms.shadow_pass.value=b.mapPass.texture,m.uniforms.resolution.value=b.mapSize,m.uniforms.radius.value=b.radius,i.setRenderTarget(b.map),i.clear(),i.renderBufferDirect(R,null,q,m,M,null)}function _(b,R,q,T){let A=null;const I=q.isPointLight===!0?b.customDistanceMaterial:b.customDepthMaterial;if(I!==void 0)A=I;else if(A=q.isPointLight===!0?l:a,i.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0){const Y=A.uuid,J=R.uuid;let N=c[Y];N===void 0&&(N={},c[Y]=N);let B=N[J];B===void 0&&(B=A.clone(),N[J]=B,R.addEventListener("dispose",D)),A=B}if(A.visible=R.visible,A.wireframe=R.wireframe,T===Ii?A.side=R.shadowSide!==null?R.shadowSide:R.side:A.side=R.shadowSide!==null?R.shadowSide:f[R.side],A.alphaMap=R.alphaMap,A.alphaTest=R.alphaTest,A.map=R.map,A.clipShadows=R.clipShadows,A.clippingPlanes=R.clippingPlanes,A.clipIntersection=R.clipIntersection,A.displacementMap=R.displacementMap,A.displacementScale=R.displacementScale,A.displacementBias=R.displacementBias,A.wireframeLinewidth=R.wireframeLinewidth,A.linewidth=R.linewidth,q.isPointLight===!0&&A.isMeshDistanceMaterial===!0){const Y=i.properties.get(A);Y.light=q}return A}function y(b,R,q,T,A){if(b.visible===!1)return;if(b.layers.test(R.layers)&&(b.isMesh||b.isLine||b.isPoints)&&(b.castShadow||b.receiveShadow&&A===Ii)&&(!b.frustumCulled||n.intersectsObject(b))){b.modelViewMatrix.multiplyMatrices(q.matrixWorldInverse,b.matrixWorld);const J=e.update(b),N=b.material;if(Array.isArray(N)){const B=J.groups;for(let V=0,W=B.length;V<W;V++){const ie=B[V],te=N[ie.materialIndex];if(te&&te.visible){const Q=_(b,te,T,A);b.onBeforeShadow(i,b,R,q,J,Q,ie),i.renderBufferDirect(q,null,J,Q,b,ie),b.onAfterShadow(i,b,R,q,J,Q,ie)}}}else if(N.visible){const B=_(b,N,T,A);b.onBeforeShadow(i,b,R,q,J,B,null),i.renderBufferDirect(q,null,J,B,b,null),b.onAfterShadow(i,b,R,q,J,B,null)}}const Y=b.children;for(let J=0,N=Y.length;J<N;J++)y(Y[J],R,q,T,A)}function D(b){b.target.removeEventListener("dispose",D);for(const q in c){const T=c[q],A=b.target.uuid;A in T&&(T[A].dispose(),delete T[A])}}}function YM(i,e,t){const n=t.isWebGL2;function r(){let F=!1;const me=new an;let Te=null;const Xe=new an(0,0,0,0);return{setMask:function(He){Te!==He&&!F&&(i.colorMask(He,He,He,He),Te=He)},setLocked:function(He){F=He},setClear:function(He,st,ot,Nt,St){St===!0&&(He*=Nt,st*=Nt,ot*=Nt),me.set(He,st,ot,Nt),Xe.equals(me)===!1&&(i.clearColor(He,st,ot,Nt),Xe.copy(me))},reset:function(){F=!1,Te=null,Xe.set(-1,0,0,0)}}}function s(){let F=!1,me=null,Te=null,Xe=null;return{setTest:function(He){He?Be(i.DEPTH_TEST):be(i.DEPTH_TEST)},setMask:function(He){me!==He&&!F&&(i.depthMask(He),me=He)},setFunc:function(He){if(Te!==He){switch(He){case dg:i.depthFunc(i.NEVER);break;case pg:i.depthFunc(i.ALWAYS);break;case mg:i.depthFunc(i.LESS);break;case qa:i.depthFunc(i.LEQUAL);break;case gg:i.depthFunc(i.EQUAL);break;case _g:i.depthFunc(i.GEQUAL);break;case vg:i.depthFunc(i.GREATER);break;case xg:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}Te=He}},setLocked:function(He){F=He},setClear:function(He){Xe!==He&&(i.clearDepth(He),Xe=He)},reset:function(){F=!1,me=null,Te=null,Xe=null}}}function o(){let F=!1,me=null,Te=null,Xe=null,He=null,st=null,ot=null,Nt=null,St=null;return{setTest:function(je){F||(je?Be(i.STENCIL_TEST):be(i.STENCIL_TEST))},setMask:function(je){me!==je&&!F&&(i.stencilMask(je),me=je)},setFunc:function(je,gt,ln){(Te!==je||Xe!==gt||He!==ln)&&(i.stencilFunc(je,gt,ln),Te=je,Xe=gt,He=ln)},setOp:function(je,gt,ln){(st!==je||ot!==gt||Nt!==ln)&&(i.stencilOp(je,gt,ln),st=je,ot=gt,Nt=ln)},setLocked:function(je){F=je},setClear:function(je){St!==je&&(i.clearStencil(je),St=je)},reset:function(){F=!1,me=null,Te=null,Xe=null,He=null,st=null,ot=null,Nt=null,St=null}}}const a=new r,l=new s,c=new o,u=new WeakMap,f=new WeakMap;let d={},m={},v=new WeakMap,M=[],p=null,h=!1,x=null,_=null,y=null,D=null,b=null,R=null,q=null,T=new ft(0,0,0),A=0,I=!1,Y=null,J=null,N=null,B=null,V=null;const W=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let ie=!1,te=0;const Q=i.getParameter(i.VERSION);Q.indexOf("WebGL")!==-1?(te=parseFloat(/^WebGL (\d)/.exec(Q)[1]),ie=te>=1):Q.indexOf("OpenGL ES")!==-1&&(te=parseFloat(/^OpenGL ES (\d)/.exec(Q)[1]),ie=te>=2);let ae=null,re={};const z=i.getParameter(i.SCISSOR_BOX),se=i.getParameter(i.VIEWPORT),ve=new an().fromArray(z),Se=new an().fromArray(se);function ge(F,me,Te,Xe){const He=new Uint8Array(4),st=i.createTexture();i.bindTexture(F,st),i.texParameteri(F,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(F,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let ot=0;ot<Te;ot++)n&&(F===i.TEXTURE_3D||F===i.TEXTURE_2D_ARRAY)?i.texImage3D(me,0,i.RGBA,1,1,Xe,0,i.RGBA,i.UNSIGNED_BYTE,He):i.texImage2D(me+ot,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,He);return st}const ke={};ke[i.TEXTURE_2D]=ge(i.TEXTURE_2D,i.TEXTURE_2D,1),ke[i.TEXTURE_CUBE_MAP]=ge(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),n&&(ke[i.TEXTURE_2D_ARRAY]=ge(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),ke[i.TEXTURE_3D]=ge(i.TEXTURE_3D,i.TEXTURE_3D,1,1)),a.setClear(0,0,0,1),l.setClear(1),c.setClear(0),Be(i.DEPTH_TEST),l.setFunc(qa),Ze(!1),L(vf),Be(i.CULL_FACE),Le(ar);function Be(F){d[F]!==!0&&(i.enable(F),d[F]=!0)}function be(F){d[F]!==!1&&(i.disable(F),d[F]=!1)}function Ke(F,me){return m[F]!==me?(i.bindFramebuffer(F,me),m[F]=me,n&&(F===i.DRAW_FRAMEBUFFER&&(m[i.FRAMEBUFFER]=me),F===i.FRAMEBUFFER&&(m[i.DRAW_FRAMEBUFFER]=me)),!0):!1}function j(F,me){let Te=M,Xe=!1;if(F)if(Te=v.get(me),Te===void 0&&(Te=[],v.set(me,Te)),F.isWebGLMultipleRenderTargets){const He=F.texture;if(Te.length!==He.length||Te[0]!==i.COLOR_ATTACHMENT0){for(let st=0,ot=He.length;st<ot;st++)Te[st]=i.COLOR_ATTACHMENT0+st;Te.length=He.length,Xe=!0}}else Te[0]!==i.COLOR_ATTACHMENT0&&(Te[0]=i.COLOR_ATTACHMENT0,Xe=!0);else Te[0]!==i.BACK&&(Te[0]=i.BACK,Xe=!0);Xe&&(t.isWebGL2?i.drawBuffers(Te):e.get("WEBGL_draw_buffers").drawBuffersWEBGL(Te))}function xt(F){return p!==F?(i.useProgram(F),p=F,!0):!1}const Ue={[Fr]:i.FUNC_ADD,[Jm]:i.FUNC_SUBTRACT,[Qm]:i.FUNC_REVERSE_SUBTRACT};if(n)Ue[yf]=i.MIN,Ue[Ef]=i.MAX;else{const F=e.get("EXT_blend_minmax");F!==null&&(Ue[yf]=F.MIN_EXT,Ue[Ef]=F.MAX_EXT)}const Ve={[eg]:i.ZERO,[tg]:i.ONE,[ng]:i.SRC_COLOR,[Yc]:i.SRC_ALPHA,[lg]:i.SRC_ALPHA_SATURATE,[og]:i.DST_COLOR,[rg]:i.DST_ALPHA,[ig]:i.ONE_MINUS_SRC_COLOR,[jc]:i.ONE_MINUS_SRC_ALPHA,[ag]:i.ONE_MINUS_DST_COLOR,[sg]:i.ONE_MINUS_DST_ALPHA,[cg]:i.CONSTANT_COLOR,[ug]:i.ONE_MINUS_CONSTANT_COLOR,[fg]:i.CONSTANT_ALPHA,[hg]:i.ONE_MINUS_CONSTANT_ALPHA};function Le(F,me,Te,Xe,He,st,ot,Nt,St,je){if(F===ar){h===!0&&(be(i.BLEND),h=!1);return}if(h===!1&&(Be(i.BLEND),h=!0),F!==Zm){if(F!==x||je!==I){if((_!==Fr||b!==Fr)&&(i.blendEquation(i.FUNC_ADD),_=Fr,b=Fr),je)switch(F){case Fs:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case xf:i.blendFunc(i.ONE,i.ONE);break;case Mf:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Sf:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",F);break}else switch(F){case Fs:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case xf:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Mf:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Sf:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",F);break}y=null,D=null,R=null,q=null,T.set(0,0,0),A=0,x=F,I=je}return}He=He||me,st=st||Te,ot=ot||Xe,(me!==_||He!==b)&&(i.blendEquationSeparate(Ue[me],Ue[He]),_=me,b=He),(Te!==y||Xe!==D||st!==R||ot!==q)&&(i.blendFuncSeparate(Ve[Te],Ve[Xe],Ve[st],Ve[ot]),y=Te,D=Xe,R=st,q=ot),(Nt.equals(T)===!1||St!==A)&&(i.blendColor(Nt.r,Nt.g,Nt.b,St),T.copy(Nt),A=St),x=F,I=!1}function mt(F,me){F.side===xi?be(i.CULL_FACE):Be(i.CULL_FACE);let Te=F.side===Ln;me&&(Te=!Te),Ze(Te),F.blending===Fs&&F.transparent===!1?Le(ar):Le(F.blending,F.blendEquation,F.blendSrc,F.blendDst,F.blendEquationAlpha,F.blendSrcAlpha,F.blendDstAlpha,F.blendColor,F.blendAlpha,F.premultipliedAlpha),l.setFunc(F.depthFunc),l.setTest(F.depthTest),l.setMask(F.depthWrite),a.setMask(F.colorWrite);const Xe=F.stencilWrite;c.setTest(Xe),Xe&&(c.setMask(F.stencilWriteMask),c.setFunc(F.stencilFunc,F.stencilRef,F.stencilFuncMask),c.setOp(F.stencilFail,F.stencilZFail,F.stencilZPass)),$(F.polygonOffset,F.polygonOffsetFactor,F.polygonOffsetUnits),F.alphaToCoverage===!0?Be(i.SAMPLE_ALPHA_TO_COVERAGE):be(i.SAMPLE_ALPHA_TO_COVERAGE)}function Ze(F){Y!==F&&(F?i.frontFace(i.CW):i.frontFace(i.CCW),Y=F)}function L(F){F!==jm?(Be(i.CULL_FACE),F!==J&&(F===vf?i.cullFace(i.BACK):F===$m?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):be(i.CULL_FACE),J=F}function E(F){F!==N&&(ie&&i.lineWidth(F),N=F)}function $(F,me,Te){F?(Be(i.POLYGON_OFFSET_FILL),(B!==me||V!==Te)&&(i.polygonOffset(me,Te),B=me,V=Te)):be(i.POLYGON_OFFSET_FILL)}function ue(F){F?Be(i.SCISSOR_TEST):be(i.SCISSOR_TEST)}function ce(F){F===void 0&&(F=i.TEXTURE0+W-1),ae!==F&&(i.activeTexture(F),ae=F)}function ee(F,me,Te){Te===void 0&&(ae===null?Te=i.TEXTURE0+W-1:Te=ae);let Xe=re[Te];Xe===void 0&&(Xe={type:void 0,texture:void 0},re[Te]=Xe),(Xe.type!==F||Xe.texture!==me)&&(ae!==Te&&(i.activeTexture(Te),ae=Te),i.bindTexture(F,me||ke[F]),Xe.type=F,Xe.texture=me)}function ne(){const F=re[ae];F!==void 0&&F.type!==void 0&&(i.bindTexture(F.type,null),F.type=void 0,F.texture=void 0)}function fe(){try{i.compressedTexImage2D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Me(){try{i.compressedTexImage3D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Fe(){try{i.texSubImage2D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Ye(){try{i.texSubImage3D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function le(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function rt(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Ge(){try{i.texStorage2D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Oe(){try{i.texStorage3D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function Ce(){try{i.texImage2D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function ye(){try{i.texImage3D.apply(i,arguments)}catch(F){console.error("THREE.WebGLState:",F)}}function U(F){ve.equals(F)===!1&&(i.scissor(F.x,F.y,F.z,F.w),ve.copy(F))}function pe(F){Se.equals(F)===!1&&(i.viewport(F.x,F.y,F.z,F.w),Se.copy(F))}function De(F,me){let Te=f.get(me);Te===void 0&&(Te=new WeakMap,f.set(me,Te));let Xe=Te.get(F);Xe===void 0&&(Xe=i.getUniformBlockIndex(me,F.name),Te.set(F,Xe))}function Ae(F,me){const Xe=f.get(me).get(F);u.get(me)!==Xe&&(i.uniformBlockBinding(me,Xe,F.__bindingPointIndex),u.set(me,Xe))}function he(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),n===!0&&(i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null)),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),d={},ae=null,re={},m={},v=new WeakMap,M=[],p=null,h=!1,x=null,_=null,y=null,D=null,b=null,R=null,q=null,T=new ft(0,0,0),A=0,I=!1,Y=null,J=null,N=null,B=null,V=null,ve.set(0,0,i.canvas.width,i.canvas.height),Se.set(0,0,i.canvas.width,i.canvas.height),a.reset(),l.reset(),c.reset()}return{buffers:{color:a,depth:l,stencil:c},enable:Be,disable:be,bindFramebuffer:Ke,drawBuffers:j,useProgram:xt,setBlending:Le,setMaterial:mt,setFlipSided:Ze,setCullFace:L,setLineWidth:E,setPolygonOffset:$,setScissorTest:ue,activeTexture:ce,bindTexture:ee,unbindTexture:ne,compressedTexImage2D:fe,compressedTexImage3D:Me,texImage2D:Ce,texImage3D:ye,updateUBOMapping:De,uniformBlockBinding:Ae,texStorage2D:Ge,texStorage3D:Oe,texSubImage2D:Fe,texSubImage3D:Ye,compressedTexSubImage2D:le,compressedTexSubImage3D:rt,scissor:U,viewport:pe,reset:he}}function jM(i,e,t,n,r,s,o){const a=r.isWebGL2,l=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),u=new WeakMap;let f;const d=new WeakMap;let m=!1;try{m=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function v(L,E){return m?new OffscreenCanvas(L,E):Za("canvas")}function M(L,E,$,ue){let ce=1;if((L.width>ue||L.height>ue)&&(ce=ue/Math.max(L.width,L.height)),ce<1||E===!0)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap){const ee=E?nu:Math.floor,ne=ee(ce*L.width),fe=ee(ce*L.height);f===void 0&&(f=v(ne,fe));const Me=$?v(ne,fe):f;return Me.width=ne,Me.height=fe,Me.getContext("2d").drawImage(L,0,0,ne,fe),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+L.width+"x"+L.height+") to ("+ne+"x"+fe+")."),Me}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+L.width+"x"+L.height+")."),L;return L}function p(L){return Jf(L.width)&&Jf(L.height)}function h(L){return a?!1:L.wrapS!==ui||L.wrapT!==ui||L.minFilter!==Sn&&L.minFilter!==Kn}function x(L,E){return L.generateMipmaps&&E&&L.minFilter!==Sn&&L.minFilter!==Kn}function _(L){i.generateMipmap(L)}function y(L,E,$,ue,ce=!1){if(a===!1)return E;if(L!==null){if(i[L]!==void 0)return i[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let ee=E;if(E===i.RED&&($===i.FLOAT&&(ee=i.R32F),$===i.HALF_FLOAT&&(ee=i.R16F),$===i.UNSIGNED_BYTE&&(ee=i.R8)),E===i.RED_INTEGER&&($===i.UNSIGNED_BYTE&&(ee=i.R8UI),$===i.UNSIGNED_SHORT&&(ee=i.R16UI),$===i.UNSIGNED_INT&&(ee=i.R32UI),$===i.BYTE&&(ee=i.R8I),$===i.SHORT&&(ee=i.R16I),$===i.INT&&(ee=i.R32I)),E===i.RG&&($===i.FLOAT&&(ee=i.RG32F),$===i.HALF_FLOAT&&(ee=i.RG16F),$===i.UNSIGNED_BYTE&&(ee=i.RG8)),E===i.RGBA){const ne=ce?Ya:Tt.getTransfer(ue);$===i.FLOAT&&(ee=i.RGBA32F),$===i.HALF_FLOAT&&(ee=i.RGBA16F),$===i.UNSIGNED_BYTE&&(ee=ne===It?i.SRGB8_ALPHA8:i.RGBA8),$===i.UNSIGNED_SHORT_4_4_4_4&&(ee=i.RGBA4),$===i.UNSIGNED_SHORT_5_5_5_1&&(ee=i.RGB5_A1)}return(ee===i.R16F||ee===i.R32F||ee===i.RG16F||ee===i.RG32F||ee===i.RGBA16F||ee===i.RGBA32F)&&e.get("EXT_color_buffer_float"),ee}function D(L,E,$){return x(L,$)===!0||L.isFramebufferTexture&&L.minFilter!==Sn&&L.minFilter!==Kn?Math.log2(Math.max(E.width,E.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?E.mipmaps.length:1}function b(L){return L===Sn||L===Tf||L===Fl?i.NEAREST:i.LINEAR}function R(L){const E=L.target;E.removeEventListener("dispose",R),T(E),E.isVideoTexture&&u.delete(E)}function q(L){const E=L.target;E.removeEventListener("dispose",q),I(E)}function T(L){const E=n.get(L);if(E.__webglInit===void 0)return;const $=L.source,ue=d.get($);if(ue){const ce=ue[E.__cacheKey];ce.usedTimes--,ce.usedTimes===0&&A(L),Object.keys(ue).length===0&&d.delete($)}n.remove(L)}function A(L){const E=n.get(L);i.deleteTexture(E.__webglTexture);const $=L.source,ue=d.get($);delete ue[E.__cacheKey],o.memory.textures--}function I(L){const E=L.texture,$=n.get(L),ue=n.get(E);if(ue.__webglTexture!==void 0&&(i.deleteTexture(ue.__webglTexture),o.memory.textures--),L.depthTexture&&L.depthTexture.dispose(),L.isWebGLCubeRenderTarget)for(let ce=0;ce<6;ce++){if(Array.isArray($.__webglFramebuffer[ce]))for(let ee=0;ee<$.__webglFramebuffer[ce].length;ee++)i.deleteFramebuffer($.__webglFramebuffer[ce][ee]);else i.deleteFramebuffer($.__webglFramebuffer[ce]);$.__webglDepthbuffer&&i.deleteRenderbuffer($.__webglDepthbuffer[ce])}else{if(Array.isArray($.__webglFramebuffer))for(let ce=0;ce<$.__webglFramebuffer.length;ce++)i.deleteFramebuffer($.__webglFramebuffer[ce]);else i.deleteFramebuffer($.__webglFramebuffer);if($.__webglDepthbuffer&&i.deleteRenderbuffer($.__webglDepthbuffer),$.__webglMultisampledFramebuffer&&i.deleteFramebuffer($.__webglMultisampledFramebuffer),$.__webglColorRenderbuffer)for(let ce=0;ce<$.__webglColorRenderbuffer.length;ce++)$.__webglColorRenderbuffer[ce]&&i.deleteRenderbuffer($.__webglColorRenderbuffer[ce]);$.__webglDepthRenderbuffer&&i.deleteRenderbuffer($.__webglDepthRenderbuffer)}if(L.isWebGLMultipleRenderTargets)for(let ce=0,ee=E.length;ce<ee;ce++){const ne=n.get(E[ce]);ne.__webglTexture&&(i.deleteTexture(ne.__webglTexture),o.memory.textures--),n.remove(E[ce])}n.remove(E),n.remove(L)}let Y=0;function J(){Y=0}function N(){const L=Y;return L>=r.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+r.maxTextures),Y+=1,L}function B(L){const E=[];return E.push(L.wrapS),E.push(L.wrapT),E.push(L.wrapR||0),E.push(L.magFilter),E.push(L.minFilter),E.push(L.anisotropy),E.push(L.internalFormat),E.push(L.format),E.push(L.type),E.push(L.generateMipmaps),E.push(L.premultiplyAlpha),E.push(L.flipY),E.push(L.unpackAlignment),E.push(L.colorSpace),E.join()}function V(L,E){const $=n.get(L);if(L.isVideoTexture&&mt(L),L.isRenderTargetTexture===!1&&L.version>0&&$.__version!==L.version){const ue=L.image;if(ue===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ue.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ve($,L,E);return}}t.bindTexture(i.TEXTURE_2D,$.__webglTexture,i.TEXTURE0+E)}function W(L,E){const $=n.get(L);if(L.version>0&&$.__version!==L.version){ve($,L,E);return}t.bindTexture(i.TEXTURE_2D_ARRAY,$.__webglTexture,i.TEXTURE0+E)}function ie(L,E){const $=n.get(L);if(L.version>0&&$.__version!==L.version){ve($,L,E);return}t.bindTexture(i.TEXTURE_3D,$.__webglTexture,i.TEXTURE0+E)}function te(L,E){const $=n.get(L);if(L.version>0&&$.__version!==L.version){Se($,L,E);return}t.bindTexture(i.TEXTURE_CUBE_MAP,$.__webglTexture,i.TEXTURE0+E)}const Q={[Zc]:i.REPEAT,[ui]:i.CLAMP_TO_EDGE,[Jc]:i.MIRRORED_REPEAT},ae={[Sn]:i.NEAREST,[Tf]:i.NEAREST_MIPMAP_NEAREST,[Fl]:i.NEAREST_MIPMAP_LINEAR,[Kn]:i.LINEAR,[Rg]:i.LINEAR_MIPMAP_NEAREST,[No]:i.LINEAR_MIPMAP_LINEAR},re={[Hg]:i.NEVER,[Yg]:i.ALWAYS,[Gg]:i.LESS,[lp]:i.LEQUAL,[Vg]:i.EQUAL,[qg]:i.GEQUAL,[Wg]:i.GREATER,[Xg]:i.NOTEQUAL};function z(L,E,$){if($?(i.texParameteri(L,i.TEXTURE_WRAP_S,Q[E.wrapS]),i.texParameteri(L,i.TEXTURE_WRAP_T,Q[E.wrapT]),(L===i.TEXTURE_3D||L===i.TEXTURE_2D_ARRAY)&&i.texParameteri(L,i.TEXTURE_WRAP_R,Q[E.wrapR]),i.texParameteri(L,i.TEXTURE_MAG_FILTER,ae[E.magFilter]),i.texParameteri(L,i.TEXTURE_MIN_FILTER,ae[E.minFilter])):(i.texParameteri(L,i.TEXTURE_WRAP_S,i.CLAMP_TO_EDGE),i.texParameteri(L,i.TEXTURE_WRAP_T,i.CLAMP_TO_EDGE),(L===i.TEXTURE_3D||L===i.TEXTURE_2D_ARRAY)&&i.texParameteri(L,i.TEXTURE_WRAP_R,i.CLAMP_TO_EDGE),(E.wrapS!==ui||E.wrapT!==ui)&&console.warn("THREE.WebGLRenderer: Texture is not power of two. Texture.wrapS and Texture.wrapT should be set to THREE.ClampToEdgeWrapping."),i.texParameteri(L,i.TEXTURE_MAG_FILTER,b(E.magFilter)),i.texParameteri(L,i.TEXTURE_MIN_FILTER,b(E.minFilter)),E.minFilter!==Sn&&E.minFilter!==Kn&&console.warn("THREE.WebGLRenderer: Texture is not power of two. Texture.minFilter should be set to THREE.NearestFilter or THREE.LinearFilter.")),E.compareFunction&&(i.texParameteri(L,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(L,i.TEXTURE_COMPARE_FUNC,re[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){const ue=e.get("EXT_texture_filter_anisotropic");if(E.magFilter===Sn||E.minFilter!==Fl&&E.minFilter!==No||E.type===or&&e.has("OES_texture_float_linear")===!1||a===!1&&E.type===Fo&&e.has("OES_texture_half_float_linear")===!1)return;(E.anisotropy>1||n.get(E).__currentAnisotropy)&&(i.texParameterf(L,ue.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,r.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy)}}function se(L,E){let $=!1;L.__webglInit===void 0&&(L.__webglInit=!0,E.addEventListener("dispose",R));const ue=E.source;let ce=d.get(ue);ce===void 0&&(ce={},d.set(ue,ce));const ee=B(E);if(ee!==L.__cacheKey){ce[ee]===void 0&&(ce[ee]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,$=!0),ce[ee].usedTimes++;const ne=ce[L.__cacheKey];ne!==void 0&&(ce[L.__cacheKey].usedTimes--,ne.usedTimes===0&&A(E)),L.__cacheKey=ee,L.__webglTexture=ce[ee].texture}return $}function ve(L,E,$){let ue=i.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(ue=i.TEXTURE_2D_ARRAY),E.isData3DTexture&&(ue=i.TEXTURE_3D);const ce=se(L,E),ee=E.source;t.bindTexture(ue,L.__webglTexture,i.TEXTURE0+$);const ne=n.get(ee);if(ee.version!==ne.__version||ce===!0){t.activeTexture(i.TEXTURE0+$);const fe=Tt.getPrimaries(Tt.workingColorSpace),Me=E.colorSpace===Qn?null:Tt.getPrimaries(E.colorSpace),Fe=E.colorSpace===Qn||fe===Me?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Fe);const Ye=h(E)&&p(E.image)===!1;let le=M(E.image,Ye,!1,r.maxTextureSize);le=Ze(E,le);const rt=p(le)||a,Ge=s.convert(E.format,E.colorSpace);let Oe=s.convert(E.type),Ce=y(E.internalFormat,Ge,Oe,E.colorSpace,E.isVideoTexture);z(ue,E,rt);let ye;const U=E.mipmaps,pe=a&&E.isVideoTexture!==!0&&Ce!==op,De=ne.__version===void 0||ce===!0,Ae=D(E,le,rt);if(E.isDepthTexture)Ce=i.DEPTH_COMPONENT,a?E.type===or?Ce=i.DEPTH_COMPONENT32F:E.type===sr?Ce=i.DEPTH_COMPONENT24:E.type===kr?Ce=i.DEPTH24_STENCIL8:Ce=i.DEPTH_COMPONENT16:E.type===or&&console.error("WebGLRenderer: Floating point depth texture requires WebGL2."),E.format===Hr&&Ce===i.DEPTH_COMPONENT&&E.type!==vu&&E.type!==sr&&(console.warn("THREE.WebGLRenderer: Use UnsignedShortType or UnsignedIntType for DepthFormat DepthTexture."),E.type=sr,Oe=s.convert(E.type)),E.format===Gs&&Ce===i.DEPTH_COMPONENT&&(Ce=i.DEPTH_STENCIL,E.type!==kr&&(console.warn("THREE.WebGLRenderer: Use UnsignedInt248Type for DepthStencilFormat DepthTexture."),E.type=kr,Oe=s.convert(E.type))),De&&(pe?t.texStorage2D(i.TEXTURE_2D,1,Ce,le.width,le.height):t.texImage2D(i.TEXTURE_2D,0,Ce,le.width,le.height,0,Ge,Oe,null));else if(E.isDataTexture)if(U.length>0&&rt){pe&&De&&t.texStorage2D(i.TEXTURE_2D,Ae,Ce,U[0].width,U[0].height);for(let he=0,F=U.length;he<F;he++)ye=U[he],pe?t.texSubImage2D(i.TEXTURE_2D,he,0,0,ye.width,ye.height,Ge,Oe,ye.data):t.texImage2D(i.TEXTURE_2D,he,Ce,ye.width,ye.height,0,Ge,Oe,ye.data);E.generateMipmaps=!1}else pe?(De&&t.texStorage2D(i.TEXTURE_2D,Ae,Ce,le.width,le.height),t.texSubImage2D(i.TEXTURE_2D,0,0,0,le.width,le.height,Ge,Oe,le.data)):t.texImage2D(i.TEXTURE_2D,0,Ce,le.width,le.height,0,Ge,Oe,le.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){pe&&De&&t.texStorage3D(i.TEXTURE_2D_ARRAY,Ae,Ce,U[0].width,U[0].height,le.depth);for(let he=0,F=U.length;he<F;he++)ye=U[he],E.format!==fi?Ge!==null?pe?t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,he,0,0,0,ye.width,ye.height,le.depth,Ge,ye.data,0,0):t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,he,Ce,ye.width,ye.height,le.depth,0,ye.data,0,0):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):pe?t.texSubImage3D(i.TEXTURE_2D_ARRAY,he,0,0,0,ye.width,ye.height,le.depth,Ge,Oe,ye.data):t.texImage3D(i.TEXTURE_2D_ARRAY,he,Ce,ye.width,ye.height,le.depth,0,Ge,Oe,ye.data)}else{pe&&De&&t.texStorage2D(i.TEXTURE_2D,Ae,Ce,U[0].width,U[0].height);for(let he=0,F=U.length;he<F;he++)ye=U[he],E.format!==fi?Ge!==null?pe?t.compressedTexSubImage2D(i.TEXTURE_2D,he,0,0,ye.width,ye.height,Ge,ye.data):t.compressedTexImage2D(i.TEXTURE_2D,he,Ce,ye.width,ye.height,0,ye.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):pe?t.texSubImage2D(i.TEXTURE_2D,he,0,0,ye.width,ye.height,Ge,Oe,ye.data):t.texImage2D(i.TEXTURE_2D,he,Ce,ye.width,ye.height,0,Ge,Oe,ye.data)}else if(E.isDataArrayTexture)pe?(De&&t.texStorage3D(i.TEXTURE_2D_ARRAY,Ae,Ce,le.width,le.height,le.depth),t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,le.width,le.height,le.depth,Ge,Oe,le.data)):t.texImage3D(i.TEXTURE_2D_ARRAY,0,Ce,le.width,le.height,le.depth,0,Ge,Oe,le.data);else if(E.isData3DTexture)pe?(De&&t.texStorage3D(i.TEXTURE_3D,Ae,Ce,le.width,le.height,le.depth),t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,le.width,le.height,le.depth,Ge,Oe,le.data)):t.texImage3D(i.TEXTURE_3D,0,Ce,le.width,le.height,le.depth,0,Ge,Oe,le.data);else if(E.isFramebufferTexture){if(De)if(pe)t.texStorage2D(i.TEXTURE_2D,Ae,Ce,le.width,le.height);else{let he=le.width,F=le.height;for(let me=0;me<Ae;me++)t.texImage2D(i.TEXTURE_2D,me,Ce,he,F,0,Ge,Oe,null),he>>=1,F>>=1}}else if(U.length>0&&rt){pe&&De&&t.texStorage2D(i.TEXTURE_2D,Ae,Ce,U[0].width,U[0].height);for(let he=0,F=U.length;he<F;he++)ye=U[he],pe?t.texSubImage2D(i.TEXTURE_2D,he,0,0,Ge,Oe,ye):t.texImage2D(i.TEXTURE_2D,he,Ce,Ge,Oe,ye);E.generateMipmaps=!1}else pe?(De&&t.texStorage2D(i.TEXTURE_2D,Ae,Ce,le.width,le.height),t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ge,Oe,le)):t.texImage2D(i.TEXTURE_2D,0,Ce,Ge,Oe,le);x(E,rt)&&_(ue),ne.__version=ee.version,E.onUpdate&&E.onUpdate(E)}L.__version=E.version}function Se(L,E,$){if(E.image.length!==6)return;const ue=se(L,E),ce=E.source;t.bindTexture(i.TEXTURE_CUBE_MAP,L.__webglTexture,i.TEXTURE0+$);const ee=n.get(ce);if(ce.version!==ee.__version||ue===!0){t.activeTexture(i.TEXTURE0+$);const ne=Tt.getPrimaries(Tt.workingColorSpace),fe=E.colorSpace===Qn?null:Tt.getPrimaries(E.colorSpace),Me=E.colorSpace===Qn||ne===fe?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,E.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,E.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Me);const Fe=E.isCompressedTexture||E.image[0].isCompressedTexture,Ye=E.image[0]&&E.image[0].isDataTexture,le=[];for(let he=0;he<6;he++)!Fe&&!Ye?le[he]=M(E.image[he],!1,!0,r.maxCubemapSize):le[he]=Ye?E.image[he].image:E.image[he],le[he]=Ze(E,le[he]);const rt=le[0],Ge=p(rt)||a,Oe=s.convert(E.format,E.colorSpace),Ce=s.convert(E.type),ye=y(E.internalFormat,Oe,Ce,E.colorSpace),U=a&&E.isVideoTexture!==!0,pe=ee.__version===void 0||ue===!0;let De=D(E,rt,Ge);z(i.TEXTURE_CUBE_MAP,E,Ge);let Ae;if(Fe){U&&pe&&t.texStorage2D(i.TEXTURE_CUBE_MAP,De,ye,rt.width,rt.height);for(let he=0;he<6;he++){Ae=le[he].mipmaps;for(let F=0;F<Ae.length;F++){const me=Ae[F];E.format!==fi?Oe!==null?U?t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F,0,0,me.width,me.height,Oe,me.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F,ye,me.width,me.height,0,me.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):U?t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F,0,0,me.width,me.height,Oe,Ce,me.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F,ye,me.width,me.height,0,Oe,Ce,me.data)}}}else{Ae=E.mipmaps,U&&pe&&(Ae.length>0&&De++,t.texStorage2D(i.TEXTURE_CUBE_MAP,De,ye,le[0].width,le[0].height));for(let he=0;he<6;he++)if(Ye){U?t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,0,0,0,le[he].width,le[he].height,Oe,Ce,le[he].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,0,ye,le[he].width,le[he].height,0,Oe,Ce,le[he].data);for(let F=0;F<Ae.length;F++){const Te=Ae[F].image[he].image;U?t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F+1,0,0,Te.width,Te.height,Oe,Ce,Te.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F+1,ye,Te.width,Te.height,0,Oe,Ce,Te.data)}}else{U?t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,0,0,0,Oe,Ce,le[he]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,0,ye,Oe,Ce,le[he]);for(let F=0;F<Ae.length;F++){const me=Ae[F];U?t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F+1,0,0,Oe,Ce,me.image[he]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+he,F+1,ye,Oe,Ce,me.image[he])}}}x(E,Ge)&&_(i.TEXTURE_CUBE_MAP),ee.__version=ce.version,E.onUpdate&&E.onUpdate(E)}L.__version=E.version}function ge(L,E,$,ue,ce,ee){const ne=s.convert($.format,$.colorSpace),fe=s.convert($.type),Me=y($.internalFormat,ne,fe,$.colorSpace);if(!n.get(E).__hasExternalTextures){const Ye=Math.max(1,E.width>>ee),le=Math.max(1,E.height>>ee);ce===i.TEXTURE_3D||ce===i.TEXTURE_2D_ARRAY?t.texImage3D(ce,ee,Me,Ye,le,E.depth,0,ne,fe,null):t.texImage2D(ce,ee,Me,Ye,le,0,ne,fe,null)}t.bindFramebuffer(i.FRAMEBUFFER,L),Le(E)?l.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,ue,ce,n.get($).__webglTexture,0,Ve(E)):(ce===i.TEXTURE_2D||ce>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&ce<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,ue,ce,n.get($).__webglTexture,ee),t.bindFramebuffer(i.FRAMEBUFFER,null)}function ke(L,E,$){if(i.bindRenderbuffer(i.RENDERBUFFER,L),E.depthBuffer&&!E.stencilBuffer){let ue=a===!0?i.DEPTH_COMPONENT24:i.DEPTH_COMPONENT16;if($||Le(E)){const ce=E.depthTexture;ce&&ce.isDepthTexture&&(ce.type===or?ue=i.DEPTH_COMPONENT32F:ce.type===sr&&(ue=i.DEPTH_COMPONENT24));const ee=Ve(E);Le(E)?l.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ee,ue,E.width,E.height):i.renderbufferStorageMultisample(i.RENDERBUFFER,ee,ue,E.width,E.height)}else i.renderbufferStorage(i.RENDERBUFFER,ue,E.width,E.height);i.framebufferRenderbuffer(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.RENDERBUFFER,L)}else if(E.depthBuffer&&E.stencilBuffer){const ue=Ve(E);$&&Le(E)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,ue,i.DEPTH24_STENCIL8,E.width,E.height):Le(E)?l.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ue,i.DEPTH24_STENCIL8,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,i.DEPTH_STENCIL,E.width,E.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.RENDERBUFFER,L)}else{const ue=E.isWebGLMultipleRenderTargets===!0?E.texture:[E.texture];for(let ce=0;ce<ue.length;ce++){const ee=ue[ce],ne=s.convert(ee.format,ee.colorSpace),fe=s.convert(ee.type),Me=y(ee.internalFormat,ne,fe,ee.colorSpace),Fe=Ve(E);$&&Le(E)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,Fe,Me,E.width,E.height):Le(E)?l.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Fe,Me,E.width,E.height):i.renderbufferStorage(i.RENDERBUFFER,Me,E.width,E.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function Be(L,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,L),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(E.depthTexture).__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),V(E.depthTexture,0);const ue=n.get(E.depthTexture).__webglTexture,ce=Ve(E);if(E.depthTexture.format===Hr)Le(E)?l.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ue,0,ce):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ue,0);else if(E.depthTexture.format===Gs)Le(E)?l.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ue,0,ce):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ue,0);else throw new Error("Unknown depthTexture format")}function be(L){const E=n.get(L),$=L.isWebGLCubeRenderTarget===!0;if(L.depthTexture&&!E.__autoAllocateDepthBuffer){if($)throw new Error("target.depthTexture not supported in Cube render targets");Be(E.__webglFramebuffer,L)}else if($){E.__webglDepthbuffer=[];for(let ue=0;ue<6;ue++)t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer[ue]),E.__webglDepthbuffer[ue]=i.createRenderbuffer(),ke(E.__webglDepthbuffer[ue],L,!1)}else t.bindFramebuffer(i.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer=i.createRenderbuffer(),ke(E.__webglDepthbuffer,L,!1);t.bindFramebuffer(i.FRAMEBUFFER,null)}function Ke(L,E,$){const ue=n.get(L);E!==void 0&&ge(ue.__webglFramebuffer,L,L.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),$!==void 0&&be(L)}function j(L){const E=L.texture,$=n.get(L),ue=n.get(E);L.addEventListener("dispose",q),L.isWebGLMultipleRenderTargets!==!0&&(ue.__webglTexture===void 0&&(ue.__webglTexture=i.createTexture()),ue.__version=E.version,o.memory.textures++);const ce=L.isWebGLCubeRenderTarget===!0,ee=L.isWebGLMultipleRenderTargets===!0,ne=p(L)||a;if(ce){$.__webglFramebuffer=[];for(let fe=0;fe<6;fe++)if(a&&E.mipmaps&&E.mipmaps.length>0){$.__webglFramebuffer[fe]=[];for(let Me=0;Me<E.mipmaps.length;Me++)$.__webglFramebuffer[fe][Me]=i.createFramebuffer()}else $.__webglFramebuffer[fe]=i.createFramebuffer()}else{if(a&&E.mipmaps&&E.mipmaps.length>0){$.__webglFramebuffer=[];for(let fe=0;fe<E.mipmaps.length;fe++)$.__webglFramebuffer[fe]=i.createFramebuffer()}else $.__webglFramebuffer=i.createFramebuffer();if(ee)if(r.drawBuffers){const fe=L.texture;for(let Me=0,Fe=fe.length;Me<Fe;Me++){const Ye=n.get(fe[Me]);Ye.__webglTexture===void 0&&(Ye.__webglTexture=i.createTexture(),o.memory.textures++)}}else console.warn("THREE.WebGLRenderer: WebGLMultipleRenderTargets can only be used with WebGL2 or WEBGL_draw_buffers extension.");if(a&&L.samples>0&&Le(L)===!1){const fe=ee?E:[E];$.__webglMultisampledFramebuffer=i.createFramebuffer(),$.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,$.__webglMultisampledFramebuffer);for(let Me=0;Me<fe.length;Me++){const Fe=fe[Me];$.__webglColorRenderbuffer[Me]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,$.__webglColorRenderbuffer[Me]);const Ye=s.convert(Fe.format,Fe.colorSpace),le=s.convert(Fe.type),rt=y(Fe.internalFormat,Ye,le,Fe.colorSpace,L.isXRRenderTarget===!0),Ge=Ve(L);i.renderbufferStorageMultisample(i.RENDERBUFFER,Ge,rt,L.width,L.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Me,i.RENDERBUFFER,$.__webglColorRenderbuffer[Me])}i.bindRenderbuffer(i.RENDERBUFFER,null),L.depthBuffer&&($.__webglDepthRenderbuffer=i.createRenderbuffer(),ke($.__webglDepthRenderbuffer,L,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(ce){t.bindTexture(i.TEXTURE_CUBE_MAP,ue.__webglTexture),z(i.TEXTURE_CUBE_MAP,E,ne);for(let fe=0;fe<6;fe++)if(a&&E.mipmaps&&E.mipmaps.length>0)for(let Me=0;Me<E.mipmaps.length;Me++)ge($.__webglFramebuffer[fe][Me],L,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+fe,Me);else ge($.__webglFramebuffer[fe],L,E,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+fe,0);x(E,ne)&&_(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(ee){const fe=L.texture;for(let Me=0,Fe=fe.length;Me<Fe;Me++){const Ye=fe[Me],le=n.get(Ye);t.bindTexture(i.TEXTURE_2D,le.__webglTexture),z(i.TEXTURE_2D,Ye,ne),ge($.__webglFramebuffer,L,Ye,i.COLOR_ATTACHMENT0+Me,i.TEXTURE_2D,0),x(Ye,ne)&&_(i.TEXTURE_2D)}t.unbindTexture()}else{let fe=i.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(a?fe=L.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY:console.error("THREE.WebGLTextures: THREE.Data3DTexture and THREE.DataArrayTexture only supported with WebGL2.")),t.bindTexture(fe,ue.__webglTexture),z(fe,E,ne),a&&E.mipmaps&&E.mipmaps.length>0)for(let Me=0;Me<E.mipmaps.length;Me++)ge($.__webglFramebuffer[Me],L,E,i.COLOR_ATTACHMENT0,fe,Me);else ge($.__webglFramebuffer,L,E,i.COLOR_ATTACHMENT0,fe,0);x(E,ne)&&_(fe),t.unbindTexture()}L.depthBuffer&&be(L)}function xt(L){const E=p(L)||a,$=L.isWebGLMultipleRenderTargets===!0?L.texture:[L.texture];for(let ue=0,ce=$.length;ue<ce;ue++){const ee=$[ue];if(x(ee,E)){const ne=L.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:i.TEXTURE_2D,fe=n.get(ee).__webglTexture;t.bindTexture(ne,fe),_(ne),t.unbindTexture()}}}function Ue(L){if(a&&L.samples>0&&Le(L)===!1){const E=L.isWebGLMultipleRenderTargets?L.texture:[L.texture],$=L.width,ue=L.height;let ce=i.COLOR_BUFFER_BIT;const ee=[],ne=L.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,fe=n.get(L),Me=L.isWebGLMultipleRenderTargets===!0;if(Me)for(let Fe=0;Fe<E.length;Fe++)t.bindFramebuffer(i.FRAMEBUFFER,fe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Fe,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,fe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Fe,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,fe.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,fe.__webglFramebuffer);for(let Fe=0;Fe<E.length;Fe++){ee.push(i.COLOR_ATTACHMENT0+Fe),L.depthBuffer&&ee.push(ne);const Ye=fe.__ignoreDepthValues!==void 0?fe.__ignoreDepthValues:!1;if(Ye===!1&&(L.depthBuffer&&(ce|=i.DEPTH_BUFFER_BIT),L.stencilBuffer&&(ce|=i.STENCIL_BUFFER_BIT)),Me&&i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,fe.__webglColorRenderbuffer[Fe]),Ye===!0&&(i.invalidateFramebuffer(i.READ_FRAMEBUFFER,[ne]),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[ne])),Me){const le=n.get(E[Fe]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,le,0)}i.blitFramebuffer(0,0,$,ue,0,0,$,ue,ce,i.NEAREST),c&&i.invalidateFramebuffer(i.READ_FRAMEBUFFER,ee)}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),Me)for(let Fe=0;Fe<E.length;Fe++){t.bindFramebuffer(i.FRAMEBUFFER,fe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Fe,i.RENDERBUFFER,fe.__webglColorRenderbuffer[Fe]);const Ye=n.get(E[Fe]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,fe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Fe,i.TEXTURE_2D,Ye,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,fe.__webglMultisampledFramebuffer)}}function Ve(L){return Math.min(r.maxSamples,L.samples)}function Le(L){const E=n.get(L);return a&&L.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function mt(L){const E=o.render.frame;u.get(L)!==E&&(u.set(L,E),L.update())}function Ze(L,E){const $=L.colorSpace,ue=L.format,ce=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||L.format===eu||$!==Wi&&$!==Qn&&(Tt.getTransfer($)===It?a===!1?e.has("EXT_sRGB")===!0&&ue===fi?(L.format=eu,L.minFilter=Kn,L.generateMipmaps=!1):E=up.sRGBToLinear(E):(ue!==fi||ce!==cr)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",$)),E}this.allocateTextureUnit=N,this.resetTextureUnits=J,this.setTexture2D=V,this.setTexture2DArray=W,this.setTexture3D=ie,this.setTextureCube=te,this.rebindTextures=Ke,this.setupRenderTarget=j,this.updateRenderTargetMipmap=xt,this.updateMultisampleRenderTarget=Ue,this.setupDepthRenderbuffer=be,this.setupFrameBufferTexture=ge,this.useMultisampledRTT=Le}function $M(i,e,t){const n=t.isWebGL2;function r(s,o=Qn){let a;const l=Tt.getTransfer(o);if(s===cr)return i.UNSIGNED_BYTE;if(s===tp)return i.UNSIGNED_SHORT_4_4_4_4;if(s===np)return i.UNSIGNED_SHORT_5_5_5_1;if(s===Cg)return i.BYTE;if(s===Lg)return i.SHORT;if(s===vu)return i.UNSIGNED_SHORT;if(s===ep)return i.INT;if(s===sr)return i.UNSIGNED_INT;if(s===or)return i.FLOAT;if(s===Fo)return n?i.HALF_FLOAT:(a=e.get("OES_texture_half_float"),a!==null?a.HALF_FLOAT_OES:null);if(s===Pg)return i.ALPHA;if(s===fi)return i.RGBA;if(s===Dg)return i.LUMINANCE;if(s===Ug)return i.LUMINANCE_ALPHA;if(s===Hr)return i.DEPTH_COMPONENT;if(s===Gs)return i.DEPTH_STENCIL;if(s===eu)return a=e.get("EXT_sRGB"),a!==null?a.SRGB_ALPHA_EXT:null;if(s===Ig)return i.RED;if(s===ip)return i.RED_INTEGER;if(s===Ng)return i.RG;if(s===rp)return i.RG_INTEGER;if(s===sp)return i.RGBA_INTEGER;if(s===Ol||s===Bl||s===zl||s===kl)if(l===It)if(a=e.get("WEBGL_compressed_texture_s3tc_srgb"),a!==null){if(s===Ol)return a.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(s===Bl)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(s===zl)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(s===kl)return a.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(a=e.get("WEBGL_compressed_texture_s3tc"),a!==null){if(s===Ol)return a.COMPRESSED_RGB_S3TC_DXT1_EXT;if(s===Bl)return a.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(s===zl)return a.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(s===kl)return a.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(s===bf||s===Af||s===wf||s===Rf)if(a=e.get("WEBGL_compressed_texture_pvrtc"),a!==null){if(s===bf)return a.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(s===Af)return a.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(s===wf)return a.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(s===Rf)return a.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(s===op)return a=e.get("WEBGL_compressed_texture_etc1"),a!==null?a.COMPRESSED_RGB_ETC1_WEBGL:null;if(s===Cf||s===Lf)if(a=e.get("WEBGL_compressed_texture_etc"),a!==null){if(s===Cf)return l===It?a.COMPRESSED_SRGB8_ETC2:a.COMPRESSED_RGB8_ETC2;if(s===Lf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:a.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(s===Pf||s===Df||s===Uf||s===If||s===Nf||s===Ff||s===Of||s===Bf||s===zf||s===kf||s===Hf||s===Gf||s===Vf||s===Wf)if(a=e.get("WEBGL_compressed_texture_astc"),a!==null){if(s===Pf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:a.COMPRESSED_RGBA_ASTC_4x4_KHR;if(s===Df)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:a.COMPRESSED_RGBA_ASTC_5x4_KHR;if(s===Uf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:a.COMPRESSED_RGBA_ASTC_5x5_KHR;if(s===If)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:a.COMPRESSED_RGBA_ASTC_6x5_KHR;if(s===Nf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:a.COMPRESSED_RGBA_ASTC_6x6_KHR;if(s===Ff)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:a.COMPRESSED_RGBA_ASTC_8x5_KHR;if(s===Of)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:a.COMPRESSED_RGBA_ASTC_8x6_KHR;if(s===Bf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:a.COMPRESSED_RGBA_ASTC_8x8_KHR;if(s===zf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:a.COMPRESSED_RGBA_ASTC_10x5_KHR;if(s===kf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:a.COMPRESSED_RGBA_ASTC_10x6_KHR;if(s===Hf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:a.COMPRESSED_RGBA_ASTC_10x8_KHR;if(s===Gf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:a.COMPRESSED_RGBA_ASTC_10x10_KHR;if(s===Vf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:a.COMPRESSED_RGBA_ASTC_12x10_KHR;if(s===Wf)return l===It?a.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:a.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(s===Hl||s===Xf||s===qf)if(a=e.get("EXT_texture_compression_bptc"),a!==null){if(s===Hl)return l===It?a.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:a.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(s===Xf)return a.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(s===qf)return a.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(s===Fg||s===Yf||s===jf||s===$f)if(a=e.get("EXT_texture_compression_rgtc"),a!==null){if(s===Hl)return a.COMPRESSED_RED_RGTC1_EXT;if(s===Yf)return a.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(s===jf)return a.COMPRESSED_RED_GREEN_RGTC2_EXT;if(s===$f)return a.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return s===kr?n?i.UNSIGNED_INT_24_8:(a=e.get("WEBGL_depth_texture"),a!==null?a.UNSIGNED_INT_24_8_WEBGL:null):i[s]!==void 0?i[s]:null}return{convert:r}}class KM extends Jn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class To extends Zt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const ZM={type:"move"};class fc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new To,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new To,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new k,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new k),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new To,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new k,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new k),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let r=null,s=null,o=null;const a=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){o=!0;for(const M of e.hand.values()){const p=t.getJointPose(M,n),h=this._getHandJoint(c,M);p!==null&&(h.matrix.fromArray(p.transform.matrix),h.matrix.decompose(h.position,h.rotation,h.scale),h.matrixWorldNeedsUpdate=!0,h.jointRadius=p.radius),h.visible=p!==null}const u=c.joints["index-finger-tip"],f=c.joints["thumb-tip"],d=u.position.distanceTo(f.position),m=.02,v=.005;c.inputState.pinching&&d>m+v?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&d<=m-v&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));a!==null&&(r=t.getPose(e.targetRaySpace,n),r===null&&s!==null&&(r=s),r!==null&&(a.matrix.fromArray(r.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,r.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(r.linearVelocity)):a.hasLinearVelocity=!1,r.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(r.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(ZM)))}return a!==null&&(a.visible=r!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new To;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}class JM extends jr{constructor(e,t){super();const n=this;let r=null,s=1,o=null,a="local-floor",l=1,c=null,u=null,f=null,d=null,m=null,v=null;const M=t.getContextAttributes();let p=null,h=null;const x=[],_=[],y=new qe;let D=null;const b=new Jn;b.layers.enable(1),b.viewport=new an;const R=new Jn;R.layers.enable(2),R.viewport=new an;const q=[b,R],T=new KM;T.layers.enable(1),T.layers.enable(2);let A=null,I=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(z){let se=x[z];return se===void 0&&(se=new fc,x[z]=se),se.getTargetRaySpace()},this.getControllerGrip=function(z){let se=x[z];return se===void 0&&(se=new fc,x[z]=se),se.getGripSpace()},this.getHand=function(z){let se=x[z];return se===void 0&&(se=new fc,x[z]=se),se.getHandSpace()};function Y(z){const se=_.indexOf(z.inputSource);if(se===-1)return;const ve=x[se];ve!==void 0&&(ve.update(z.inputSource,z.frame,c||o),ve.dispatchEvent({type:z.type,data:z.inputSource}))}function J(){r.removeEventListener("select",Y),r.removeEventListener("selectstart",Y),r.removeEventListener("selectend",Y),r.removeEventListener("squeeze",Y),r.removeEventListener("squeezestart",Y),r.removeEventListener("squeezeend",Y),r.removeEventListener("end",J),r.removeEventListener("inputsourceschange",N);for(let z=0;z<x.length;z++){const se=_[z];se!==null&&(_[z]=null,x[z].disconnect(se))}A=null,I=null,e.setRenderTarget(p),m=null,d=null,f=null,r=null,h=null,re.stop(),n.isPresenting=!1,e.setPixelRatio(D),e.setSize(y.width,y.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(z){s=z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(z){a=z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||o},this.setReferenceSpace=function(z){c=z},this.getBaseLayer=function(){return d!==null?d:m},this.getBinding=function(){return f},this.getFrame=function(){return v},this.getSession=function(){return r},this.setSession=async function(z){if(r=z,r!==null){if(p=e.getRenderTarget(),r.addEventListener("select",Y),r.addEventListener("selectstart",Y),r.addEventListener("selectend",Y),r.addEventListener("squeeze",Y),r.addEventListener("squeezestart",Y),r.addEventListener("squeezeend",Y),r.addEventListener("end",J),r.addEventListener("inputsourceschange",N),M.xrCompatible!==!0&&await t.makeXRCompatible(),D=e.getPixelRatio(),e.getSize(y),r.renderState.layers===void 0||e.capabilities.isWebGL2===!1){const se={antialias:r.renderState.layers===void 0?M.antialias:!0,alpha:!0,depth:M.depth,stencil:M.stencil,framebufferScaleFactor:s};m=new XRWebGLLayer(r,t,se),r.updateRenderState({baseLayer:m}),e.setPixelRatio(1),e.setSize(m.framebufferWidth,m.framebufferHeight,!1),h=new Xr(m.framebufferWidth,m.framebufferHeight,{format:fi,type:cr,colorSpace:e.outputColorSpace,stencilBuffer:M.stencil})}else{let se=null,ve=null,Se=null;M.depth&&(Se=M.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,se=M.stencil?Gs:Hr,ve=M.stencil?kr:sr);const ge={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};f=new XRWebGLBinding(r,t),d=f.createProjectionLayer(ge),r.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),h=new Xr(d.textureWidth,d.textureHeight,{format:fi,type:cr,depthTexture:new Sp(d.textureWidth,d.textureHeight,ve,void 0,void 0,void 0,void 0,void 0,void 0,se),stencilBuffer:M.stencil,colorSpace:e.outputColorSpace,samples:M.antialias?4:0});const ke=e.properties.get(h);ke.__ignoreDepthValues=d.ignoreDepthValues}h.isXRRenderTarget=!0,this.setFoveation(l),c=null,o=await r.requestReferenceSpace(a),re.setContext(r),re.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(r!==null)return r.environmentBlendMode};function N(z){for(let se=0;se<z.removed.length;se++){const ve=z.removed[se],Se=_.indexOf(ve);Se>=0&&(_[Se]=null,x[Se].disconnect(ve))}for(let se=0;se<z.added.length;se++){const ve=z.added[se];let Se=_.indexOf(ve);if(Se===-1){for(let ke=0;ke<x.length;ke++)if(ke>=_.length){_.push(ve),Se=ke;break}else if(_[ke]===null){_[ke]=ve,Se=ke;break}if(Se===-1)break}const ge=x[Se];ge&&ge.connect(ve)}}const B=new k,V=new k;function W(z,se,ve){B.setFromMatrixPosition(se.matrixWorld),V.setFromMatrixPosition(ve.matrixWorld);const Se=B.distanceTo(V),ge=se.projectionMatrix.elements,ke=ve.projectionMatrix.elements,Be=ge[14]/(ge[10]-1),be=ge[14]/(ge[10]+1),Ke=(ge[9]+1)/ge[5],j=(ge[9]-1)/ge[5],xt=(ge[8]-1)/ge[0],Ue=(ke[8]+1)/ke[0],Ve=Be*xt,Le=Be*Ue,mt=Se/(-xt+Ue),Ze=mt*-xt;se.matrixWorld.decompose(z.position,z.quaternion,z.scale),z.translateX(Ze),z.translateZ(mt),z.matrixWorld.compose(z.position,z.quaternion,z.scale),z.matrixWorldInverse.copy(z.matrixWorld).invert();const L=Be+mt,E=be+mt,$=Ve-Ze,ue=Le+(Se-Ze),ce=Ke*be/E*L,ee=j*be/E*L;z.projectionMatrix.makePerspective($,ue,ce,ee,L,E),z.projectionMatrixInverse.copy(z.projectionMatrix).invert()}function ie(z,se){se===null?z.matrixWorld.copy(z.matrix):z.matrixWorld.multiplyMatrices(se.matrixWorld,z.matrix),z.matrixWorldInverse.copy(z.matrixWorld).invert()}this.updateCamera=function(z){if(r===null)return;T.near=R.near=b.near=z.near,T.far=R.far=b.far=z.far,(A!==T.near||I!==T.far)&&(r.updateRenderState({depthNear:T.near,depthFar:T.far}),A=T.near,I=T.far);const se=z.parent,ve=T.cameras;ie(T,se);for(let Se=0;Se<ve.length;Se++)ie(ve[Se],se);ve.length===2?W(T,b,R):T.projectionMatrix.copy(b.projectionMatrix),te(z,T,se)};function te(z,se,ve){ve===null?z.matrix.copy(se.matrixWorld):(z.matrix.copy(ve.matrixWorld),z.matrix.invert(),z.matrix.multiply(se.matrixWorld)),z.matrix.decompose(z.position,z.quaternion,z.scale),z.updateMatrixWorld(!0),z.projectionMatrix.copy(se.projectionMatrix),z.projectionMatrixInverse.copy(se.projectionMatrixInverse),z.isPerspectiveCamera&&(z.fov=tu*2*Math.atan(1/z.projectionMatrix.elements[5]),z.zoom=1)}this.getCamera=function(){return T},this.getFoveation=function(){if(!(d===null&&m===null))return l},this.setFoveation=function(z){l=z,d!==null&&(d.fixedFoveation=z),m!==null&&m.fixedFoveation!==void 0&&(m.fixedFoveation=z)};let Q=null;function ae(z,se){if(u=se.getViewerPose(c||o),v=se,u!==null){const ve=u.views;m!==null&&(e.setRenderTargetFramebuffer(h,m.framebuffer),e.setRenderTarget(h));let Se=!1;ve.length!==T.cameras.length&&(T.cameras.length=0,Se=!0);for(let ge=0;ge<ve.length;ge++){const ke=ve[ge];let Be=null;if(m!==null)Be=m.getViewport(ke);else{const Ke=f.getViewSubImage(d,ke);Be=Ke.viewport,ge===0&&(e.setRenderTargetTextures(h,Ke.colorTexture,d.ignoreDepthValues?void 0:Ke.depthStencilTexture),e.setRenderTarget(h))}let be=q[ge];be===void 0&&(be=new Jn,be.layers.enable(ge),be.viewport=new an,q[ge]=be),be.matrix.fromArray(ke.transform.matrix),be.matrix.decompose(be.position,be.quaternion,be.scale),be.projectionMatrix.fromArray(ke.projectionMatrix),be.projectionMatrixInverse.copy(be.projectionMatrix).invert(),be.viewport.set(Be.x,Be.y,Be.width,Be.height),ge===0&&(T.matrix.copy(be.matrix),T.matrix.decompose(T.position,T.quaternion,T.scale)),Se===!0&&T.cameras.push(be)}}for(let ve=0;ve<x.length;ve++){const Se=_[ve],ge=x[ve];Se!==null&&ge!==void 0&&ge.update(Se,se,c||o)}Q&&Q(z,se),se.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:se}),v=null}const re=new xp;re.setAnimationLoop(ae),this.setAnimationLoop=function(z){Q=z},this.dispose=function(){}}}function QM(i,e){function t(p,h){p.matrixAutoUpdate===!0&&p.updateMatrix(),h.value.copy(p.matrix)}function n(p,h){h.color.getRGB(p.fogColor.value,gp(i)),h.isFog?(p.fogNear.value=h.near,p.fogFar.value=h.far):h.isFogExp2&&(p.fogDensity.value=h.density)}function r(p,h,x,_,y){h.isMeshBasicMaterial||h.isMeshLambertMaterial?s(p,h):h.isMeshToonMaterial?(s(p,h),f(p,h)):h.isMeshPhongMaterial?(s(p,h),u(p,h)):h.isMeshStandardMaterial?(s(p,h),d(p,h),h.isMeshPhysicalMaterial&&m(p,h,y)):h.isMeshMatcapMaterial?(s(p,h),v(p,h)):h.isMeshDepthMaterial?s(p,h):h.isMeshDistanceMaterial?(s(p,h),M(p,h)):h.isMeshNormalMaterial?s(p,h):h.isLineBasicMaterial?(o(p,h),h.isLineDashedMaterial&&a(p,h)):h.isPointsMaterial?l(p,h,x,_):h.isSpriteMaterial?c(p,h):h.isShadowMaterial?(p.color.value.copy(h.color),p.opacity.value=h.opacity):h.isShaderMaterial&&(h.uniformsNeedUpdate=!1)}function s(p,h){p.opacity.value=h.opacity,h.color&&p.diffuse.value.copy(h.color),h.emissive&&p.emissive.value.copy(h.emissive).multiplyScalar(h.emissiveIntensity),h.map&&(p.map.value=h.map,t(h.map,p.mapTransform)),h.alphaMap&&(p.alphaMap.value=h.alphaMap,t(h.alphaMap,p.alphaMapTransform)),h.bumpMap&&(p.bumpMap.value=h.bumpMap,t(h.bumpMap,p.bumpMapTransform),p.bumpScale.value=h.bumpScale,h.side===Ln&&(p.bumpScale.value*=-1)),h.normalMap&&(p.normalMap.value=h.normalMap,t(h.normalMap,p.normalMapTransform),p.normalScale.value.copy(h.normalScale),h.side===Ln&&p.normalScale.value.negate()),h.displacementMap&&(p.displacementMap.value=h.displacementMap,t(h.displacementMap,p.displacementMapTransform),p.displacementScale.value=h.displacementScale,p.displacementBias.value=h.displacementBias),h.emissiveMap&&(p.emissiveMap.value=h.emissiveMap,t(h.emissiveMap,p.emissiveMapTransform)),h.specularMap&&(p.specularMap.value=h.specularMap,t(h.specularMap,p.specularMapTransform)),h.alphaTest>0&&(p.alphaTest.value=h.alphaTest);const x=e.get(h).envMap;if(x&&(p.envMap.value=x,p.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=h.reflectivity,p.ior.value=h.ior,p.refractionRatio.value=h.refractionRatio),h.lightMap){p.lightMap.value=h.lightMap;const _=i._useLegacyLights===!0?Math.PI:1;p.lightMapIntensity.value=h.lightMapIntensity*_,t(h.lightMap,p.lightMapTransform)}h.aoMap&&(p.aoMap.value=h.aoMap,p.aoMapIntensity.value=h.aoMapIntensity,t(h.aoMap,p.aoMapTransform))}function o(p,h){p.diffuse.value.copy(h.color),p.opacity.value=h.opacity,h.map&&(p.map.value=h.map,t(h.map,p.mapTransform))}function a(p,h){p.dashSize.value=h.dashSize,p.totalSize.value=h.dashSize+h.gapSize,p.scale.value=h.scale}function l(p,h,x,_){p.diffuse.value.copy(h.color),p.opacity.value=h.opacity,p.size.value=h.size*x,p.scale.value=_*.5,h.map&&(p.map.value=h.map,t(h.map,p.uvTransform)),h.alphaMap&&(p.alphaMap.value=h.alphaMap,t(h.alphaMap,p.alphaMapTransform)),h.alphaTest>0&&(p.alphaTest.value=h.alphaTest)}function c(p,h){p.diffuse.value.copy(h.color),p.opacity.value=h.opacity,p.rotation.value=h.rotation,h.map&&(p.map.value=h.map,t(h.map,p.mapTransform)),h.alphaMap&&(p.alphaMap.value=h.alphaMap,t(h.alphaMap,p.alphaMapTransform)),h.alphaTest>0&&(p.alphaTest.value=h.alphaTest)}function u(p,h){p.specular.value.copy(h.specular),p.shininess.value=Math.max(h.shininess,1e-4)}function f(p,h){h.gradientMap&&(p.gradientMap.value=h.gradientMap)}function d(p,h){p.metalness.value=h.metalness,h.metalnessMap&&(p.metalnessMap.value=h.metalnessMap,t(h.metalnessMap,p.metalnessMapTransform)),p.roughness.value=h.roughness,h.roughnessMap&&(p.roughnessMap.value=h.roughnessMap,t(h.roughnessMap,p.roughnessMapTransform)),e.get(h).envMap&&(p.envMapIntensity.value=h.envMapIntensity)}function m(p,h,x){p.ior.value=h.ior,h.sheen>0&&(p.sheenColor.value.copy(h.sheenColor).multiplyScalar(h.sheen),p.sheenRoughness.value=h.sheenRoughness,h.sheenColorMap&&(p.sheenColorMap.value=h.sheenColorMap,t(h.sheenColorMap,p.sheenColorMapTransform)),h.sheenRoughnessMap&&(p.sheenRoughnessMap.value=h.sheenRoughnessMap,t(h.sheenRoughnessMap,p.sheenRoughnessMapTransform))),h.clearcoat>0&&(p.clearcoat.value=h.clearcoat,p.clearcoatRoughness.value=h.clearcoatRoughness,h.clearcoatMap&&(p.clearcoatMap.value=h.clearcoatMap,t(h.clearcoatMap,p.clearcoatMapTransform)),h.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=h.clearcoatRoughnessMap,t(h.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),h.clearcoatNormalMap&&(p.clearcoatNormalMap.value=h.clearcoatNormalMap,t(h.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(h.clearcoatNormalScale),h.side===Ln&&p.clearcoatNormalScale.value.negate())),h.iridescence>0&&(p.iridescence.value=h.iridescence,p.iridescenceIOR.value=h.iridescenceIOR,p.iridescenceThicknessMinimum.value=h.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=h.iridescenceThicknessRange[1],h.iridescenceMap&&(p.iridescenceMap.value=h.iridescenceMap,t(h.iridescenceMap,p.iridescenceMapTransform)),h.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=h.iridescenceThicknessMap,t(h.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),h.transmission>0&&(p.transmission.value=h.transmission,p.transmissionSamplerMap.value=x.texture,p.transmissionSamplerSize.value.set(x.width,x.height),h.transmissionMap&&(p.transmissionMap.value=h.transmissionMap,t(h.transmissionMap,p.transmissionMapTransform)),p.thickness.value=h.thickness,h.thicknessMap&&(p.thicknessMap.value=h.thicknessMap,t(h.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=h.attenuationDistance,p.attenuationColor.value.copy(h.attenuationColor)),h.anisotropy>0&&(p.anisotropyVector.value.set(h.anisotropy*Math.cos(h.anisotropyRotation),h.anisotropy*Math.sin(h.anisotropyRotation)),h.anisotropyMap&&(p.anisotropyMap.value=h.anisotropyMap,t(h.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=h.specularIntensity,p.specularColor.value.copy(h.specularColor),h.specularColorMap&&(p.specularColorMap.value=h.specularColorMap,t(h.specularColorMap,p.specularColorMapTransform)),h.specularIntensityMap&&(p.specularIntensityMap.value=h.specularIntensityMap,t(h.specularIntensityMap,p.specularIntensityMapTransform))}function v(p,h){h.matcap&&(p.matcap.value=h.matcap)}function M(p,h){const x=e.get(h).light;p.referencePosition.value.setFromMatrixPosition(x.matrixWorld),p.nearDistance.value=x.shadow.camera.near,p.farDistance.value=x.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:r}}function eS(i,e,t,n){let r={},s={},o=[];const a=t.isWebGL2?i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS):0;function l(x,_){const y=_.program;n.uniformBlockBinding(x,y)}function c(x,_){let y=r[x.id];y===void 0&&(v(x),y=u(x),r[x.id]=y,x.addEventListener("dispose",p));const D=_.program;n.updateUBOMapping(x,D);const b=e.render.frame;s[x.id]!==b&&(d(x),s[x.id]=b)}function u(x){const _=f();x.__bindingPointIndex=_;const y=i.createBuffer(),D=x.__size,b=x.usage;return i.bindBuffer(i.UNIFORM_BUFFER,y),i.bufferData(i.UNIFORM_BUFFER,D,b),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,_,y),y}function f(){for(let x=0;x<a;x++)if(o.indexOf(x)===-1)return o.push(x),x;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(x){const _=r[x.id],y=x.uniforms,D=x.__cache;i.bindBuffer(i.UNIFORM_BUFFER,_);for(let b=0,R=y.length;b<R;b++){const q=Array.isArray(y[b])?y[b]:[y[b]];for(let T=0,A=q.length;T<A;T++){const I=q[T];if(m(I,b,T,D)===!0){const Y=I.__offset,J=Array.isArray(I.value)?I.value:[I.value];let N=0;for(let B=0;B<J.length;B++){const V=J[B],W=M(V);typeof V=="number"||typeof V=="boolean"?(I.__data[0]=V,i.bufferSubData(i.UNIFORM_BUFFER,Y+N,I.__data)):V.isMatrix3?(I.__data[0]=V.elements[0],I.__data[1]=V.elements[1],I.__data[2]=V.elements[2],I.__data[3]=0,I.__data[4]=V.elements[3],I.__data[5]=V.elements[4],I.__data[6]=V.elements[5],I.__data[7]=0,I.__data[8]=V.elements[6],I.__data[9]=V.elements[7],I.__data[10]=V.elements[8],I.__data[11]=0):(V.toArray(I.__data,N),N+=W.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,Y,I.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function m(x,_,y,D){const b=x.value,R=_+"_"+y;if(D[R]===void 0)return typeof b=="number"||typeof b=="boolean"?D[R]=b:D[R]=b.clone(),!0;{const q=D[R];if(typeof b=="number"||typeof b=="boolean"){if(q!==b)return D[R]=b,!0}else if(q.equals(b)===!1)return q.copy(b),!0}return!1}function v(x){const _=x.uniforms;let y=0;const D=16;for(let R=0,q=_.length;R<q;R++){const T=Array.isArray(_[R])?_[R]:[_[R]];for(let A=0,I=T.length;A<I;A++){const Y=T[A],J=Array.isArray(Y.value)?Y.value:[Y.value];for(let N=0,B=J.length;N<B;N++){const V=J[N],W=M(V),ie=y%D;ie!==0&&D-ie<W.boundary&&(y+=D-ie),Y.__data=new Float32Array(W.storage/Float32Array.BYTES_PER_ELEMENT),Y.__offset=y,y+=W.storage}}}const b=y%D;return b>0&&(y+=D-b),x.__size=y,x.__cache={},this}function M(x){const _={boundary:0,storage:0};return typeof x=="number"||typeof x=="boolean"?(_.boundary=4,_.storage=4):x.isVector2?(_.boundary=8,_.storage=8):x.isVector3||x.isColor?(_.boundary=16,_.storage=12):x.isVector4?(_.boundary=16,_.storage=16):x.isMatrix3?(_.boundary=48,_.storage=48):x.isMatrix4?(_.boundary=64,_.storage=64):x.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",x),_}function p(x){const _=x.target;_.removeEventListener("dispose",p);const y=o.indexOf(_.__bindingPointIndex);o.splice(y,1),i.deleteBuffer(r[_.id]),delete r[_.id],delete s[_.id]}function h(){for(const x in r)i.deleteBuffer(r[x]);o=[],r={},s={}}return{bind:l,update:c,dispose:h}}class wp{constructor(e={}){const{canvas:t=Kg(),context:n=null,depth:r=!0,stencil:s=!0,alpha:o=!1,antialias:a=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:f=!1}=e;this.isWebGLRenderer=!0;let d;n!==null?d=n.getContextAttributes().alpha:d=o;const m=new Uint32Array(4),v=new Int32Array(4);let M=null,p=null;const h=[],x=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=fn,this._useLegacyLights=!1,this.toneMapping=lr,this.toneMappingExposure=1;const _=this;let y=!1,D=0,b=0,R=null,q=-1,T=null;const A=new an,I=new an;let Y=null;const J=new ft(0);let N=0,B=t.width,V=t.height,W=1,ie=null,te=null;const Q=new an(0,0,B,V),ae=new an(0,0,B,V);let re=!1;const z=new Su;let se=!1,ve=!1,Se=null;const ge=new Bt,ke=new qe,Be=new k,be={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};function Ke(){return R===null?W:1}let j=n;function xt(w,H){for(let Z=0;Z<w.length;Z++){const K=w[Z],G=t.getContext(K,H);if(G!==null)return G}return null}try{const w={alpha:!0,depth:r,stencil:s,antialias:a,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:f};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${_u}`),t.addEventListener("webglcontextlost",he,!1),t.addEventListener("webglcontextrestored",F,!1),t.addEventListener("webglcontextcreationerror",me,!1),j===null){const H=["webgl2","webgl","experimental-webgl"];if(_.isWebGL1Renderer===!0&&H.shift(),j=xt(H,w),j===null)throw xt(H)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}typeof WebGLRenderingContext<"u"&&j instanceof WebGLRenderingContext&&console.warn("THREE.WebGLRenderer: WebGL 1 support was deprecated in r153 and will be removed in r163."),j.getShaderPrecisionFormat===void 0&&(j.getShaderPrecisionFormat=function(){return{rangeMin:1,rangeMax:1,precision:1}})}catch(w){throw console.error("THREE.WebGLRenderer: "+w.message),w}let Ue,Ve,Le,mt,Ze,L,E,$,ue,ce,ee,ne,fe,Me,Fe,Ye,le,rt,Ge,Oe,Ce,ye,U,pe;function De(){Ue=new ux(j),Ve=new rx(j,Ue,e),Ue.init(Ve),ye=new $M(j,Ue,Ve),Le=new YM(j,Ue,Ve),mt=new dx(j),Ze=new UM,L=new jM(j,Ue,Le,Ze,Ve,ye,mt),E=new ox(_),$=new cx(_),ue=new S_(j,Ve),U=new nx(j,Ue,ue,Ve),ce=new fx(j,ue,mt,U),ee=new _x(j,ce,ue,mt),Ge=new gx(j,Ve,L),Ye=new sx(Ze),ne=new DM(_,E,$,Ue,Ve,U,Ye),fe=new QM(_,Ze),Me=new NM,Fe=new HM(Ue,Ve),rt=new tx(_,E,$,Le,ee,d,l),le=new qM(_,ee,Ve),pe=new eS(j,mt,Ve,Le),Oe=new ix(j,Ue,mt,Ve),Ce=new hx(j,Ue,mt,Ve),mt.programs=ne.programs,_.capabilities=Ve,_.extensions=Ue,_.properties=Ze,_.renderLists=Me,_.shadowMap=le,_.state=Le,_.info=mt}De();const Ae=new JM(_,j);this.xr=Ae,this.getContext=function(){return j},this.getContextAttributes=function(){return j.getContextAttributes()},this.forceContextLoss=function(){const w=Ue.get("WEBGL_lose_context");w&&w.loseContext()},this.forceContextRestore=function(){const w=Ue.get("WEBGL_lose_context");w&&w.restoreContext()},this.getPixelRatio=function(){return W},this.setPixelRatio=function(w){w!==void 0&&(W=w,this.setSize(B,V,!1))},this.getSize=function(w){return w.set(B,V)},this.setSize=function(w,H,Z=!0){if(Ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}B=w,V=H,t.width=Math.floor(w*W),t.height=Math.floor(H*W),Z===!0&&(t.style.width=w+"px",t.style.height=H+"px"),this.setViewport(0,0,w,H)},this.getDrawingBufferSize=function(w){return w.set(B*W,V*W).floor()},this.setDrawingBufferSize=function(w,H,Z){B=w,V=H,W=Z,t.width=Math.floor(w*Z),t.height=Math.floor(H*Z),this.setViewport(0,0,w,H)},this.getCurrentViewport=function(w){return w.copy(A)},this.getViewport=function(w){return w.copy(Q)},this.setViewport=function(w,H,Z,K){w.isVector4?Q.set(w.x,w.y,w.z,w.w):Q.set(w,H,Z,K),Le.viewport(A.copy(Q).multiplyScalar(W).floor())},this.getScissor=function(w){return w.copy(ae)},this.setScissor=function(w,H,Z,K){w.isVector4?ae.set(w.x,w.y,w.z,w.w):ae.set(w,H,Z,K),Le.scissor(I.copy(ae).multiplyScalar(W).floor())},this.getScissorTest=function(){return re},this.setScissorTest=function(w){Le.setScissorTest(re=w)},this.setOpaqueSort=function(w){ie=w},this.setTransparentSort=function(w){te=w},this.getClearColor=function(w){return w.copy(rt.getClearColor())},this.setClearColor=function(){rt.setClearColor.apply(rt,arguments)},this.getClearAlpha=function(){return rt.getClearAlpha()},this.setClearAlpha=function(){rt.setClearAlpha.apply(rt,arguments)},this.clear=function(w=!0,H=!0,Z=!0){let K=0;if(w){let G=!1;if(R!==null){const xe=R.texture.format;G=xe===sp||xe===rp||xe===ip}if(G){const xe=R.texture.type,Ie=xe===cr||xe===sr||xe===vu||xe===kr||xe===tp||xe===np,Ne=rt.getClearColor(),We=rt.getClearAlpha(),tt=Ne.r,Je=Ne.g,Qe=Ne.b;Ie?(m[0]=tt,m[1]=Je,m[2]=Qe,m[3]=We,j.clearBufferuiv(j.COLOR,0,m)):(v[0]=tt,v[1]=Je,v[2]=Qe,v[3]=We,j.clearBufferiv(j.COLOR,0,v))}else K|=j.COLOR_BUFFER_BIT}H&&(K|=j.DEPTH_BUFFER_BIT),Z&&(K|=j.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),j.clear(K)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",he,!1),t.removeEventListener("webglcontextrestored",F,!1),t.removeEventListener("webglcontextcreationerror",me,!1),Me.dispose(),Fe.dispose(),Ze.dispose(),E.dispose(),$.dispose(),ee.dispose(),U.dispose(),pe.dispose(),ne.dispose(),Ae.dispose(),Ae.removeEventListener("sessionstart",St),Ae.removeEventListener("sessionend",je),Se&&(Se.dispose(),Se=null),gt.stop()};function he(w){w.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),y=!0}function F(){console.log("THREE.WebGLRenderer: Context Restored."),y=!1;const w=mt.autoReset,H=le.enabled,Z=le.autoUpdate,K=le.needsUpdate,G=le.type;De(),mt.autoReset=w,le.enabled=H,le.autoUpdate=Z,le.needsUpdate=K,le.type=G}function me(w){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",w.statusMessage)}function Te(w){const H=w.target;H.removeEventListener("dispose",Te),Xe(H)}function Xe(w){He(w),Ze.remove(w)}function He(w){const H=Ze.get(w).programs;H!==void 0&&(H.forEach(function(Z){ne.releaseProgram(Z)}),w.isShaderMaterial&&ne.releaseShaderCache(w))}this.renderBufferDirect=function(w,H,Z,K,G,xe){H===null&&(H=be);const Ie=G.isMesh&&G.matrixWorld.determinant()<0,Ne=yl(w,H,Z,K,G);Le.setMaterial(K,Ie);let We=Z.index,tt=1;if(K.wireframe===!0){if(We=ce.getWireframeAttribute(Z),We===void 0)return;tt=2}const Je=Z.drawRange,Qe=Z.attributes.position;let yt=Je.start*tt,cn=(Je.start+Je.count)*tt;xe!==null&&(yt=Math.max(yt,xe.start*tt),cn=Math.min(cn,(xe.start+xe.count)*tt)),We!==null?(yt=Math.max(yt,0),cn=Math.min(cn,We.count)):Qe!=null&&(yt=Math.max(yt,0),cn=Math.min(cn,Qe.count));const zt=cn-yt;if(zt<0||zt===1/0)return;U.setup(G,K,Ne,Z,We);let Dn,bt=Oe;if(We!==null&&(Dn=ue.get(We),bt=Ce,bt.setIndex(Dn)),G.isMesh)K.wireframe===!0?(Le.setLineWidth(K.wireframeLinewidth*Ke()),bt.setMode(j.LINES)):bt.setMode(j.TRIANGLES);else if(G.isLine){let nt=K.linewidth;nt===void 0&&(nt=1),Le.setLineWidth(nt*Ke()),G.isLineSegments?bt.setMode(j.LINES):G.isLineLoop?bt.setMode(j.LINE_LOOP):bt.setMode(j.LINE_STRIP)}else G.isPoints?bt.setMode(j.POINTS):G.isSprite&&bt.setMode(j.TRIANGLES);if(G.isBatchedMesh)bt.renderMultiDraw(G._multiDrawStarts,G._multiDrawCounts,G._multiDrawCount);else if(G.isInstancedMesh)bt.renderInstances(yt,zt,G.count);else if(Z.isInstancedBufferGeometry){const nt=Z._maxInstanceCount!==void 0?Z._maxInstanceCount:1/0,yr=Math.min(Z.instanceCount,nt);bt.renderInstances(yt,zt,yr)}else bt.render(yt,zt)};function st(w,H,Z){w.transparent===!0&&w.side===xi&&w.forceSinglePass===!1?(w.side=Ln,w.needsUpdate=!0,Sr(w,H,Z),w.side=gr,w.needsUpdate=!0,Sr(w,H,Z),w.side=xi):Sr(w,H,Z)}this.compile=function(w,H,Z=null){Z===null&&(Z=w),p=Fe.get(Z),p.init(),x.push(p),Z.traverseVisible(function(G){G.isLight&&G.layers.test(H.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),w!==Z&&w.traverseVisible(function(G){G.isLight&&G.layers.test(H.layers)&&(p.pushLight(G),G.castShadow&&p.pushShadow(G))}),p.setupLights(_._useLegacyLights);const K=new Set;return w.traverse(function(G){const xe=G.material;if(xe)if(Array.isArray(xe))for(let Ie=0;Ie<xe.length;Ie++){const Ne=xe[Ie];st(Ne,Z,G),K.add(Ne)}else st(xe,Z,G),K.add(xe)}),x.pop(),p=null,K},this.compileAsync=function(w,H,Z=null){const K=this.compile(w,H,Z);return new Promise(G=>{function xe(){if(K.forEach(function(Ie){Ze.get(Ie).currentProgram.isReady()&&K.delete(Ie)}),K.size===0){G(w);return}setTimeout(xe,10)}Ue.get("KHR_parallel_shader_compile")!==null?xe():setTimeout(xe,10)})};let ot=null;function Nt(w){ot&&ot(w)}function St(){gt.stop()}function je(){gt.start()}const gt=new xp;gt.setAnimationLoop(Nt),typeof self<"u"&&gt.setContext(self),this.setAnimationLoop=function(w){ot=w,Ae.setAnimationLoop(w),w===null?gt.stop():gt.start()},Ae.addEventListener("sessionstart",St),Ae.addEventListener("sessionend",je),this.render=function(w,H){if(H!==void 0&&H.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(y===!0)return;w.matrixWorldAutoUpdate===!0&&w.updateMatrixWorld(),H.parent===null&&H.matrixWorldAutoUpdate===!0&&H.updateMatrixWorld(),Ae.enabled===!0&&Ae.isPresenting===!0&&(Ae.cameraAutoUpdate===!0&&Ae.updateCamera(H),H=Ae.getCamera()),w.isScene===!0&&w.onBeforeRender(_,w,H,R),p=Fe.get(w,x.length),p.init(),x.push(p),ge.multiplyMatrices(H.projectionMatrix,H.matrixWorldInverse),z.setFromProjectionMatrix(ge),ve=this.localClippingEnabled,se=Ye.init(this.clippingPlanes,ve),M=Me.get(w,h.length),M.init(),h.push(M),ln(w,H,0,_.sortObjects),M.finish(),_.sortObjects===!0&&M.sort(ie,te),this.info.render.frame++,se===!0&&Ye.beginShadows();const Z=p.state.shadowsArray;if(le.render(Z,w,H),se===!0&&Ye.endShadows(),this.info.autoReset===!0&&this.info.reset(),rt.render(M,w),p.setupLights(_._useLegacyLights),H.isArrayCamera){const K=H.cameras;for(let G=0,xe=K.length;G<xe;G++){const Ie=K[G];Si(M,w,Ie,Ie.viewport)}}else Si(M,w,H);R!==null&&(L.updateMultisampleRenderTarget(R),L.updateRenderTargetMipmap(R)),w.isScene===!0&&w.onAfterRender(_,w,H),U.resetDefaultState(),q=-1,T=null,x.pop(),x.length>0?p=x[x.length-1]:p=null,h.pop(),h.length>0?M=h[h.length-1]:M=null};function ln(w,H,Z,K){if(w.visible===!1)return;if(w.layers.test(H.layers)){if(w.isGroup)Z=w.renderOrder;else if(w.isLOD)w.autoUpdate===!0&&w.update(H);else if(w.isLight)p.pushLight(w),w.castShadow&&p.pushShadow(w);else if(w.isSprite){if(!w.frustumCulled||z.intersectsSprite(w)){K&&Be.setFromMatrixPosition(w.matrixWorld).applyMatrix4(ge);const Ie=ee.update(w),Ne=w.material;Ne.visible&&M.push(w,Ie,Ne,Z,Be.z,null)}}else if((w.isMesh||w.isLine||w.isPoints)&&(!w.frustumCulled||z.intersectsObject(w))){const Ie=ee.update(w),Ne=w.material;if(K&&(w.boundingSphere!==void 0?(w.boundingSphere===null&&w.computeBoundingSphere(),Be.copy(w.boundingSphere.center)):(Ie.boundingSphere===null&&Ie.computeBoundingSphere(),Be.copy(Ie.boundingSphere.center)),Be.applyMatrix4(w.matrixWorld).applyMatrix4(ge)),Array.isArray(Ne)){const We=Ie.groups;for(let tt=0,Je=We.length;tt<Je;tt++){const Qe=We[tt],yt=Ne[Qe.materialIndex];yt&&yt.visible&&M.push(w,Ie,yt,Z,Be.z,Qe)}}else Ne.visible&&M.push(w,Ie,Ne,Z,Be.z,null)}}const xe=w.children;for(let Ie=0,Ne=xe.length;Ie<Ne;Ie++)ln(xe[Ie],H,Z,K)}function Si(w,H,Z,K){const G=w.opaque,xe=w.transmissive,Ie=w.transparent;p.setupLightsView(Z),se===!0&&Ye.setGlobalState(_.clippingPlanes,Z),xe.length>0&&wn(G,xe,H,Z),K&&Le.viewport(A.copy(K)),G.length>0&&ti(G,H,Z),xe.length>0&&ti(xe,H,Z),Ie.length>0&&ti(Ie,H,Z),Le.buffers.depth.setTest(!0),Le.buffers.depth.setMask(!0),Le.buffers.color.setMask(!0),Le.setPolygonOffset(!1)}function wn(w,H,Z,K){if((Z.isScene===!0?Z.overrideMaterial:null)!==null)return;const xe=Ve.isWebGL2;Se===null&&(Se=new Xr(1,1,{generateMipmaps:!0,type:Ue.has("EXT_color_buffer_half_float")?Fo:cr,minFilter:No,samples:xe?4:0})),_.getDrawingBufferSize(ke),xe?Se.setSize(ke.x,ke.y):Se.setSize(nu(ke.x),nu(ke.y));const Ie=_.getRenderTarget();_.setRenderTarget(Se),_.getClearColor(J),N=_.getClearAlpha(),N<1&&_.setClearColor(16777215,.5),_.clear();const Ne=_.toneMapping;_.toneMapping=lr,ti(w,Z,K),L.updateMultisampleRenderTarget(Se),L.updateRenderTargetMipmap(Se);let We=!1;for(let tt=0,Je=H.length;tt<Je;tt++){const Qe=H[tt],yt=Qe.object,cn=Qe.geometry,zt=Qe.material,Dn=Qe.group;if(zt.side===xi&&yt.layers.test(K.layers)){const bt=zt.side;zt.side=Ln,zt.needsUpdate=!0,yi(yt,Z,K,cn,zt,Dn),zt.side=bt,zt.needsUpdate=!0,We=!0}}We===!0&&(L.updateMultisampleRenderTarget(Se),L.updateRenderTargetMipmap(Se)),_.setRenderTarget(Ie),_.setClearColor(J,N),_.toneMapping=Ne}function ti(w,H,Z){const K=H.isScene===!0?H.overrideMaterial:null;for(let G=0,xe=w.length;G<xe;G++){const Ie=w[G],Ne=Ie.object,We=Ie.geometry,tt=K===null?Ie.material:K,Je=Ie.group;Ne.layers.test(Z.layers)&&yi(Ne,H,Z,We,tt,Je)}}function yi(w,H,Z,K,G,xe){w.onBeforeRender(_,H,Z,K,G,xe),w.modelViewMatrix.multiplyMatrices(Z.matrixWorldInverse,w.matrixWorld),w.normalMatrix.getNormalMatrix(w.modelViewMatrix),G.onBeforeRender(_,H,Z,K,w,xe),G.transparent===!0&&G.side===xi&&G.forceSinglePass===!1?(G.side=Ln,G.needsUpdate=!0,_.renderBufferDirect(Z,H,K,G,w,xe),G.side=gr,G.needsUpdate=!0,_.renderBufferDirect(Z,H,K,G,w,xe),G.side=xi):_.renderBufferDirect(Z,H,K,G,w,xe),w.onAfterRender(_,H,Z,K,G,xe)}function Sr(w,H,Z){H.isScene!==!0&&(H=be);const K=Ze.get(w),G=p.state.lights,xe=p.state.shadowsArray,Ie=G.state.version,Ne=ne.getParameters(w,G.state,xe,H,Z),We=ne.getProgramCacheKey(Ne);let tt=K.programs;K.environment=w.isMeshStandardMaterial?H.environment:null,K.fog=H.fog,K.envMap=(w.isMeshStandardMaterial?$:E).get(w.envMap||K.environment),tt===void 0&&(w.addEventListener("dispose",Te),tt=new Map,K.programs=tt);let Je=tt.get(We);if(Je!==void 0){if(K.currentProgram===Je&&K.lightsStateVersion===Ie)return $o(w,Ne),Je}else Ne.uniforms=ne.getUniforms(w),w.onBuild(Z,Ne,_),w.onBeforeCompile(Ne,_),Je=ne.acquireProgram(Ne,We),tt.set(We,Je),K.uniforms=Ne.uniforms;const Qe=K.uniforms;return(!w.isShaderMaterial&&!w.isRawShaderMaterial||w.clipping===!0)&&(Qe.clippingPlanes=Ye.uniform),$o(w,Ne),K.needsLights=El(w),K.lightsStateVersion=Ie,K.needsLights&&(Qe.ambientLightColor.value=G.state.ambient,Qe.lightProbe.value=G.state.probe,Qe.directionalLights.value=G.state.directional,Qe.directionalLightShadows.value=G.state.directionalShadow,Qe.spotLights.value=G.state.spot,Qe.spotLightShadows.value=G.state.spotShadow,Qe.rectAreaLights.value=G.state.rectArea,Qe.ltc_1.value=G.state.rectAreaLTC1,Qe.ltc_2.value=G.state.rectAreaLTC2,Qe.pointLights.value=G.state.point,Qe.pointLightShadows.value=G.state.pointShadow,Qe.hemisphereLights.value=G.state.hemi,Qe.directionalShadowMap.value=G.state.directionalShadowMap,Qe.directionalShadowMatrix.value=G.state.directionalShadowMatrix,Qe.spotShadowMap.value=G.state.spotShadowMap,Qe.spotLightMatrix.value=G.state.spotLightMatrix,Qe.spotLightMap.value=G.state.spotLightMap,Qe.pointShadowMap.value=G.state.pointShadowMap,Qe.pointShadowMatrix.value=G.state.pointShadowMatrix),K.currentProgram=Je,K.uniformsList=null,Je}function to(w){if(w.uniformsList===null){const H=w.currentProgram.getUniforms();w.uniformsList=Va.seqWithValue(H.seq,w.uniforms)}return w.uniformsList}function $o(w,H){const Z=Ze.get(w);Z.outputColorSpace=H.outputColorSpace,Z.batching=H.batching,Z.instancing=H.instancing,Z.instancingColor=H.instancingColor,Z.skinning=H.skinning,Z.morphTargets=H.morphTargets,Z.morphNormals=H.morphNormals,Z.morphColors=H.morphColors,Z.morphTargetsCount=H.morphTargetsCount,Z.numClippingPlanes=H.numClippingPlanes,Z.numIntersection=H.numClipIntersection,Z.vertexAlphas=H.vertexAlphas,Z.vertexTangents=H.vertexTangents,Z.toneMapping=H.toneMapping}function yl(w,H,Z,K,G){H.isScene!==!0&&(H=be),L.resetTextureUnits();const xe=H.fog,Ie=K.isMeshStandardMaterial?H.environment:null,Ne=R===null?_.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:Wi,We=(K.isMeshStandardMaterial?$:E).get(K.envMap||Ie),tt=K.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,Je=!!Z.attributes.tangent&&(!!K.normalMap||K.anisotropy>0),Qe=!!Z.morphAttributes.position,yt=!!Z.morphAttributes.normal,cn=!!Z.morphAttributes.color;let zt=lr;K.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(zt=_.toneMapping);const Dn=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,bt=Dn!==void 0?Dn.length:0,nt=Ze.get(K),yr=p.state.lights;if(se===!0&&(ve===!0||w!==T)){const Rn=w===T&&K.id===q;Ye.setState(K,w,Rn)}let Ct=!1;K.version===nt.__version?(nt.needsLights&&nt.lightsStateVersion!==yr.state.version||nt.outputColorSpace!==Ne||G.isBatchedMesh&&nt.batching===!1||!G.isBatchedMesh&&nt.batching===!0||G.isInstancedMesh&&nt.instancing===!1||!G.isInstancedMesh&&nt.instancing===!0||G.isSkinnedMesh&&nt.skinning===!1||!G.isSkinnedMesh&&nt.skinning===!0||G.isInstancedMesh&&nt.instancingColor===!0&&G.instanceColor===null||G.isInstancedMesh&&nt.instancingColor===!1&&G.instanceColor!==null||nt.envMap!==We||K.fog===!0&&nt.fog!==xe||nt.numClippingPlanes!==void 0&&(nt.numClippingPlanes!==Ye.numPlanes||nt.numIntersection!==Ye.numIntersection)||nt.vertexAlphas!==tt||nt.vertexTangents!==Je||nt.morphTargets!==Qe||nt.morphNormals!==yt||nt.morphColors!==cn||nt.toneMapping!==zt||Ve.isWebGL2===!0&&nt.morphTargetsCount!==bt)&&(Ct=!0):(Ct=!0,nt.__version=K.version);let kt=nt.currentProgram;Ct===!0&&(kt=Sr(K,H,G));let no=!1,qi=!1,Er=!1;const Yt=kt.getUniforms(),Ti=nt.uniforms;if(Le.useProgram(kt.program)&&(no=!0,qi=!0,Er=!0),K.id!==q&&(q=K.id,qi=!0),no||T!==w){Yt.setValue(j,"projectionMatrix",w.projectionMatrix),Yt.setValue(j,"viewMatrix",w.matrixWorldInverse);const Rn=Yt.map.cameraPosition;Rn!==void 0&&Rn.setValue(j,Be.setFromMatrixPosition(w.matrixWorld)),Ve.logarithmicDepthBuffer&&Yt.setValue(j,"logDepthBufFC",2/(Math.log(w.far+1)/Math.LN2)),(K.isMeshPhongMaterial||K.isMeshToonMaterial||K.isMeshLambertMaterial||K.isMeshBasicMaterial||K.isMeshStandardMaterial||K.isShaderMaterial)&&Yt.setValue(j,"isOrthographic",w.isOrthographicCamera===!0),T!==w&&(T=w,qi=!0,Er=!0)}if(G.isSkinnedMesh){Yt.setOptional(j,G,"bindMatrix"),Yt.setOptional(j,G,"bindMatrixInverse");const Rn=G.skeleton;Rn&&(Ve.floatVertexTextures?(Rn.boneTexture===null&&Rn.computeBoneTexture(),Yt.setValue(j,"boneTexture",Rn.boneTexture,L)):console.warn("THREE.WebGLRenderer: SkinnedMesh can only be used with WebGL 2. With WebGL 1 OES_texture_float and vertex textures support is required."))}G.isBatchedMesh&&(Yt.setOptional(j,G,"batchingTexture"),Yt.setValue(j,"batchingTexture",G._matricesTexture,L));const io=Z.morphAttributes;if((io.position!==void 0||io.normal!==void 0||io.color!==void 0&&Ve.isWebGL2===!0)&&Ge.update(G,Z,kt),(qi||nt.receiveShadow!==G.receiveShadow)&&(nt.receiveShadow=G.receiveShadow,Yt.setValue(j,"receiveShadow",G.receiveShadow)),K.isMeshGouraudMaterial&&K.envMap!==null&&(Ti.envMap.value=We,Ti.flipEnvMap.value=We.isCubeTexture&&We.isRenderTargetTexture===!1?-1:1),qi&&(Yt.setValue(j,"toneMappingExposure",_.toneMappingExposure),nt.needsLights&&Ei(Ti,Er),xe&&K.fog===!0&&fe.refreshFogUniforms(Ti,xe),fe.refreshMaterialUniforms(Ti,K,W,V,Se),Va.upload(j,to(nt),Ti,L)),K.isShaderMaterial&&K.uniformsNeedUpdate===!0&&(Va.upload(j,to(nt),Ti,L),K.uniformsNeedUpdate=!1),K.isSpriteMaterial&&Yt.setValue(j,"center",G.center),Yt.setValue(j,"modelViewMatrix",G.modelViewMatrix),Yt.setValue(j,"normalMatrix",G.normalMatrix),Yt.setValue(j,"modelMatrix",G.matrixWorld),K.isShaderMaterial||K.isRawShaderMaterial){const Rn=K.uniformsGroups;for(let Jr=0,Ko=Rn.length;Jr<Ko;Jr++)if(Ve.isWebGL2){const Zo=Rn[Jr];pe.update(Zo,kt),pe.bind(Zo,kt)}else console.warn("THREE.WebGLRenderer: Uniform Buffer Objects can only be used with WebGL 2.")}return kt}function Ei(w,H){w.ambientLightColor.needsUpdate=H,w.lightProbe.needsUpdate=H,w.directionalLights.needsUpdate=H,w.directionalLightShadows.needsUpdate=H,w.pointLights.needsUpdate=H,w.pointLightShadows.needsUpdate=H,w.spotLights.needsUpdate=H,w.spotLightShadows.needsUpdate=H,w.rectAreaLights.needsUpdate=H,w.hemisphereLights.needsUpdate=H}function El(w){return w.isMeshLambertMaterial||w.isMeshToonMaterial||w.isMeshPhongMaterial||w.isMeshStandardMaterial||w.isShadowMaterial||w.isShaderMaterial&&w.lights===!0}this.getActiveCubeFace=function(){return D},this.getActiveMipmapLevel=function(){return b},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(w,H,Z){Ze.get(w.texture).__webglTexture=H,Ze.get(w.depthTexture).__webglTexture=Z;const K=Ze.get(w);K.__hasExternalTextures=!0,K.__hasExternalTextures&&(K.__autoAllocateDepthBuffer=Z===void 0,K.__autoAllocateDepthBuffer||Ue.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),K.__useRenderToTexture=!1))},this.setRenderTargetFramebuffer=function(w,H){const Z=Ze.get(w);Z.__webglFramebuffer=H,Z.__useDefaultFramebuffer=H===void 0},this.setRenderTarget=function(w,H=0,Z=0){R=w,D=H,b=Z;let K=!0,G=null,xe=!1,Ie=!1;if(w){const We=Ze.get(w);We.__useDefaultFramebuffer!==void 0?(Le.bindFramebuffer(j.FRAMEBUFFER,null),K=!1):We.__webglFramebuffer===void 0?L.setupRenderTarget(w):We.__hasExternalTextures&&L.rebindTextures(w,Ze.get(w.texture).__webglTexture,Ze.get(w.depthTexture).__webglTexture);const tt=w.texture;(tt.isData3DTexture||tt.isDataArrayTexture||tt.isCompressedArrayTexture)&&(Ie=!0);const Je=Ze.get(w).__webglFramebuffer;w.isWebGLCubeRenderTarget?(Array.isArray(Je[H])?G=Je[H][Z]:G=Je[H],xe=!0):Ve.isWebGL2&&w.samples>0&&L.useMultisampledRTT(w)===!1?G=Ze.get(w).__webglMultisampledFramebuffer:Array.isArray(Je)?G=Je[Z]:G=Je,A.copy(w.viewport),I.copy(w.scissor),Y=w.scissorTest}else A.copy(Q).multiplyScalar(W).floor(),I.copy(ae).multiplyScalar(W).floor(),Y=re;if(Le.bindFramebuffer(j.FRAMEBUFFER,G)&&Ve.drawBuffers&&K&&Le.drawBuffers(w,G),Le.viewport(A),Le.scissor(I),Le.setScissorTest(Y),xe){const We=Ze.get(w.texture);j.framebufferTexture2D(j.FRAMEBUFFER,j.COLOR_ATTACHMENT0,j.TEXTURE_CUBE_MAP_POSITIVE_X+H,We.__webglTexture,Z)}else if(Ie){const We=Ze.get(w.texture),tt=H||0;j.framebufferTextureLayer(j.FRAMEBUFFER,j.COLOR_ATTACHMENT0,We.__webglTexture,Z||0,tt)}q=-1},this.readRenderTargetPixels=function(w,H,Z,K,G,xe,Ie){if(!(w&&w.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Ne=Ze.get(w).__webglFramebuffer;if(w.isWebGLCubeRenderTarget&&Ie!==void 0&&(Ne=Ne[Ie]),Ne){Le.bindFramebuffer(j.FRAMEBUFFER,Ne);try{const We=w.texture,tt=We.format,Je=We.type;if(tt!==fi&&ye.convert(tt)!==j.getParameter(j.IMPLEMENTATION_COLOR_READ_FORMAT)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}const Qe=Je===Fo&&(Ue.has("EXT_color_buffer_half_float")||Ve.isWebGL2&&Ue.has("EXT_color_buffer_float"));if(Je!==cr&&ye.convert(Je)!==j.getParameter(j.IMPLEMENTATION_COLOR_READ_TYPE)&&!(Je===or&&(Ve.isWebGL2||Ue.has("OES_texture_float")||Ue.has("WEBGL_color_buffer_float")))&&!Qe){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}H>=0&&H<=w.width-K&&Z>=0&&Z<=w.height-G&&j.readPixels(H,Z,K,G,ye.convert(tt),ye.convert(Je),xe)}finally{const We=R!==null?Ze.get(R).__webglFramebuffer:null;Le.bindFramebuffer(j.FRAMEBUFFER,We)}}},this.copyFramebufferToTexture=function(w,H,Z=0){const K=Math.pow(2,-Z),G=Math.floor(H.image.width*K),xe=Math.floor(H.image.height*K);L.setTexture2D(H,0),j.copyTexSubImage2D(j.TEXTURE_2D,Z,0,0,w.x,w.y,G,xe),Le.unbindTexture()},this.copyTextureToTexture=function(w,H,Z,K=0){const G=H.image.width,xe=H.image.height,Ie=ye.convert(Z.format),Ne=ye.convert(Z.type);L.setTexture2D(Z,0),j.pixelStorei(j.UNPACK_FLIP_Y_WEBGL,Z.flipY),j.pixelStorei(j.UNPACK_PREMULTIPLY_ALPHA_WEBGL,Z.premultiplyAlpha),j.pixelStorei(j.UNPACK_ALIGNMENT,Z.unpackAlignment),H.isDataTexture?j.texSubImage2D(j.TEXTURE_2D,K,w.x,w.y,G,xe,Ie,Ne,H.image.data):H.isCompressedTexture?j.compressedTexSubImage2D(j.TEXTURE_2D,K,w.x,w.y,H.mipmaps[0].width,H.mipmaps[0].height,Ie,H.mipmaps[0].data):j.texSubImage2D(j.TEXTURE_2D,K,w.x,w.y,Ie,Ne,H.image),K===0&&Z.generateMipmaps&&j.generateMipmap(j.TEXTURE_2D),Le.unbindTexture()},this.copyTextureToTexture3D=function(w,H,Z,K,G=0){if(_.isWebGL1Renderer){console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: can only be used with WebGL2.");return}const xe=w.max.x-w.min.x+1,Ie=w.max.y-w.min.y+1,Ne=w.max.z-w.min.z+1,We=ye.convert(K.format),tt=ye.convert(K.type);let Je;if(K.isData3DTexture)L.setTexture3D(K,0),Je=j.TEXTURE_3D;else if(K.isDataArrayTexture||K.isCompressedArrayTexture)L.setTexture2DArray(K,0),Je=j.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}j.pixelStorei(j.UNPACK_FLIP_Y_WEBGL,K.flipY),j.pixelStorei(j.UNPACK_PREMULTIPLY_ALPHA_WEBGL,K.premultiplyAlpha),j.pixelStorei(j.UNPACK_ALIGNMENT,K.unpackAlignment);const Qe=j.getParameter(j.UNPACK_ROW_LENGTH),yt=j.getParameter(j.UNPACK_IMAGE_HEIGHT),cn=j.getParameter(j.UNPACK_SKIP_PIXELS),zt=j.getParameter(j.UNPACK_SKIP_ROWS),Dn=j.getParameter(j.UNPACK_SKIP_IMAGES),bt=Z.isCompressedTexture?Z.mipmaps[G]:Z.image;j.pixelStorei(j.UNPACK_ROW_LENGTH,bt.width),j.pixelStorei(j.UNPACK_IMAGE_HEIGHT,bt.height),j.pixelStorei(j.UNPACK_SKIP_PIXELS,w.min.x),j.pixelStorei(j.UNPACK_SKIP_ROWS,w.min.y),j.pixelStorei(j.UNPACK_SKIP_IMAGES,w.min.z),Z.isDataTexture||Z.isData3DTexture?j.texSubImage3D(Je,G,H.x,H.y,H.z,xe,Ie,Ne,We,tt,bt.data):Z.isCompressedArrayTexture?(console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: untested support for compressed srcTexture."),j.compressedTexSubImage3D(Je,G,H.x,H.y,H.z,xe,Ie,Ne,We,bt.data)):j.texSubImage3D(Je,G,H.x,H.y,H.z,xe,Ie,Ne,We,tt,bt),j.pixelStorei(j.UNPACK_ROW_LENGTH,Qe),j.pixelStorei(j.UNPACK_IMAGE_HEIGHT,yt),j.pixelStorei(j.UNPACK_SKIP_PIXELS,cn),j.pixelStorei(j.UNPACK_SKIP_ROWS,zt),j.pixelStorei(j.UNPACK_SKIP_IMAGES,Dn),G===0&&K.generateMipmaps&&j.generateMipmap(Je),Le.unbindTexture()},this.initTexture=function(w){w.isCubeTexture?L.setTextureCube(w,0):w.isData3DTexture?L.setTexture3D(w,0):w.isDataArrayTexture||w.isCompressedArrayTexture?L.setTexture2DArray(w,0):L.setTexture2D(w,0),Le.unbindTexture()},this.resetState=function(){D=0,b=0,R=null,Le.reset(),U.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return zi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===xu?"display-p3":"srgb",t.unpackColorSpace=Tt.workingColorSpace===ll?"display-p3":"srgb"}get outputEncoding(){return console.warn("THREE.WebGLRenderer: Property .outputEncoding has been removed. Use .outputColorSpace instead."),this.outputColorSpace===fn?Gr:ap}set outputEncoding(e){console.warn("THREE.WebGLRenderer: Property .outputEncoding has been removed. Use .outputColorSpace instead."),this.outputColorSpace=e===Gr?fn:Wi}get useLegacyLights(){return console.warn("THREE.WebGLRenderer: The property .useLegacyLights has been deprecated. Migrate your lighting according to the following guide: https://discourse.threejs.org/t/updates-to-lighting-in-three-js-r155/53733."),this._useLegacyLights}set useLegacyLights(e){console.warn("THREE.WebGLRenderer: The property .useLegacyLights has been deprecated. Migrate your lighting according to the following guide: https://discourse.threejs.org/t/updates-to-lighting-in-three-js-r155/53733."),this._useLegacyLights=e}}class tS extends wp{}tS.prototype.isWebGL1Renderer=!0;class nS extends Zt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t}}class iS{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Qc,this._updateRange={offset:0,count:-1},this.updateRanges=[],this.version=0,this.uuid=ur()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}get updateRange(){return console.warn("THREE.InterleavedBuffer: updateRange() is deprecated and will be removed in r169. Use addUpdateRange() instead."),this._updateRange}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let r=0,s=this.stride;r<s;r++)this.array[e+r]=t.array[n+r];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=ur()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=ur()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const xn=new k;class Ja{constructor(e,t,n,r=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=r}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)xn.fromBufferAttribute(this,t),xn.applyMatrix4(e),this.setXYZ(t,xn.x,xn.y,xn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)xn.fromBufferAttribute(this,t),xn.applyNormalMatrix(e),this.setXYZ(t,xn.x,xn.y,xn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)xn.fromBufferAttribute(this,t),xn.transformDirection(e),this.setXYZ(t,xn.x,xn.y,xn.z);return this}setX(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=At(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=Oi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=Oi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=Oi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=Oi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),r=At(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this}setXYZW(e,t,n,r,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=At(t,this.array),n=At(n,this.array),r=At(r,this.array),s=At(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=r,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return new Gn(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Ja(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const r=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[r+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}class Rp extends $r{constructor(e){super(),this.isSpriteMaterial=!0,this.type="SpriteMaterial",this.color=new ft(16777215),this.map=null,this.alphaMap=null,this.rotation=0,this.sizeAttenuation=!0,this.transparent=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.rotation=e.rotation,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}let As;const po=new k,ws=new k,Rs=new k,Cs=new qe,mo=new qe,Cp=new Bt,ba=new k,go=new k,Aa=new k,Oh=new qe,hc=new qe,Bh=new qe;class rS extends Zt{constructor(e=new Rp){if(super(),this.isSprite=!0,this.type="Sprite",As===void 0){As=new An;const t=new Float32Array([-.5,-.5,0,0,0,.5,-.5,0,1,0,.5,.5,0,1,1,-.5,.5,0,0,1]),n=new iS(t,5);As.setIndex([0,1,2,0,2,3]),As.setAttribute("position",new Ja(n,3,0,!1)),As.setAttribute("uv",new Ja(n,2,3,!1))}this.geometry=As,this.material=e,this.center=new qe(.5,.5)}raycast(e,t){e.camera===null&&console.error('THREE.Sprite: "Raycaster.camera" needs to be set in order to raycast against sprites.'),ws.setFromMatrixScale(this.matrixWorld),Cp.copy(e.camera.matrixWorld),this.modelViewMatrix.multiplyMatrices(e.camera.matrixWorldInverse,this.matrixWorld),Rs.setFromMatrixPosition(this.modelViewMatrix),e.camera.isPerspectiveCamera&&this.material.sizeAttenuation===!1&&ws.multiplyScalar(-Rs.z);const n=this.material.rotation;let r,s;n!==0&&(s=Math.cos(n),r=Math.sin(n));const o=this.center;wa(ba.set(-.5,-.5,0),Rs,o,ws,r,s),wa(go.set(.5,-.5,0),Rs,o,ws,r,s),wa(Aa.set(.5,.5,0),Rs,o,ws,r,s),Oh.set(0,0),hc.set(1,0),Bh.set(1,1);let a=e.ray.intersectTriangle(ba,go,Aa,!1,po);if(a===null&&(wa(go.set(-.5,.5,0),Rs,o,ws,r,s),hc.set(0,1),a=e.ray.intersectTriangle(ba,Aa,go,!1,po),a===null))return;const l=e.ray.origin.distanceTo(po);l<e.near||l>e.far||t.push({distance:l,point:po.clone(),uv:Zn.getInterpolation(po,ba,go,Aa,Oh,hc,Bh,new qe),face:null,object:this})}copy(e,t){return super.copy(e,t),e.center!==void 0&&this.center.copy(e.center),this.material=e.material,this}}function wa(i,e,t,n,r,s){Cs.subVectors(i,t).addScalar(.5).multiply(n),r!==void 0?(mo.x=s*Cs.x-r*Cs.y,mo.y=r*Cs.x+s*Cs.y):mo.copy(Cs),i.copy(e),i.x+=mo.x,i.y+=mo.y,i.applyMatrix4(Cp)}class Lp extends $r{constructor(e){super(),this.isLineBasicMaterial=!0,this.type="LineBasicMaterial",this.color=new ft(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const zh=new k,kh=new k,Hh=new Bt,dc=new Wo,Ra=new Vo;class sS extends Zt{constructor(e=new An,t=new Lp){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let r=1,s=t.count;r<s;r++)zh.fromBufferAttribute(t,r-1),kh.fromBufferAttribute(t,r),n[r]=n[r-1],n[r]+=zh.distanceTo(kh);e.setAttribute("lineDistance",new Ot(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,r=this.matrixWorld,s=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Ra.copy(n.boundingSphere),Ra.applyMatrix4(r),Ra.radius+=s,e.ray.intersectsSphere(Ra)===!1)return;Hh.copy(r).invert(),dc.copy(e.ray).applyMatrix4(Hh);const a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=new k,u=new k,f=new k,d=new k,m=this.isLineSegments?2:1,v=n.index,p=n.attributes.position;if(v!==null){const h=Math.max(0,o.start),x=Math.min(v.count,o.start+o.count);for(let _=h,y=x-1;_<y;_+=m){const D=v.getX(_),b=v.getX(_+1);if(c.fromBufferAttribute(p,D),u.fromBufferAttribute(p,b),dc.distanceSqToSegment(c,u,d,f)>l)continue;d.applyMatrix4(this.matrixWorld);const q=e.ray.origin.distanceTo(d);q<e.near||q>e.far||t.push({distance:q,point:f.clone().applyMatrix4(this.matrixWorld),index:_,face:null,faceIndex:null,object:this})}}else{const h=Math.max(0,o.start),x=Math.min(p.count,o.start+o.count);for(let _=h,y=x-1;_<y;_+=m){if(c.fromBufferAttribute(p,_),u.fromBufferAttribute(p,_+1),dc.distanceSqToSegment(c,u,d,f)>l)continue;d.applyMatrix4(this.matrixWorld);const b=e.ray.origin.distanceTo(d);b<e.near||b>e.far||t.push({distance:b,point:f.clone().applyMatrix4(this.matrixWorld),index:_,face:null,faceIndex:null,object:this})}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=r.length;s<o;s++){const a=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}}const Gh=new k,Vh=new k;class oS extends sS{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let r=0,s=t.count;r<s;r+=2)Gh.fromBufferAttribute(t,r),Vh.fromBufferAttribute(t,r+1),n[r]=r===0?0:n[r-1],n[r+1]=n[r]+Gh.distanceTo(Vh);e.setAttribute("lineDistance",new Ot(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Tu extends $r{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new ft(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Wh=new Bt,ru=new Wo,Ca=new Vo,La=new k;class Pp extends Zt{constructor(e=new An,t=new Tu){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,r=this.matrixWorld,s=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Ca.copy(n.boundingSphere),Ca.applyMatrix4(r),Ca.radius+=s,e.ray.intersectsSphere(Ca)===!1)return;Wh.copy(r).invert(),ru.copy(e.ray).applyMatrix4(Wh);const a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=n.index,f=n.attributes.position;if(c!==null){const d=Math.max(0,o.start),m=Math.min(c.count,o.start+o.count);for(let v=d,M=m;v<M;v++){const p=c.getX(v);La.fromBufferAttribute(f,p),Xh(La,p,l,r,e,t,this)}}else{const d=Math.max(0,o.start),m=Math.min(f.count,o.start+o.count);for(let v=d,M=m;v<M;v++)La.fromBufferAttribute(f,v),Xh(La,v,l,r,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const r=t[n[0]];if(r!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=r.length;s<o;s++){const a=r[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}}function Xh(i,e,t,n,r,s,o){const a=ru.distanceSqToPoint(i);if(a<t){const l=new k;ru.closestPointToPoint(i,l),l.applyMatrix4(n);const c=r.ray.origin.distanceTo(l);if(c<r.near||c>r.far)return;s.push({distance:c,distanceToRay:Math.sqrt(a),point:l,index:e,face:null,object:o})}}class aS extends Pn{constructor(e,t,n,r,s,o,a,l,c){super(e,t,n,r,s,o,a,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}class bu extends An{constructor(e=.5,t=1,n=32,r=1,s=0,o=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:r,thetaStart:s,thetaLength:o},n=Math.max(3,n),r=Math.max(1,r);const a=[],l=[],c=[],u=[];let f=e;const d=(t-e)/r,m=new k,v=new qe;for(let M=0;M<=r;M++){for(let p=0;p<=n;p++){const h=s+p/n*o;m.x=f*Math.cos(h),m.y=f*Math.sin(h),l.push(m.x,m.y,m.z),c.push(0,0,1),v.x=(m.x/t+1)/2,v.y=(m.y/t+1)/2,u.push(v.x,v.y)}f+=d}for(let M=0;M<r;M++){const p=M*(n+1);for(let h=0;h<n;h++){const x=h+p,_=x,y=x+n+1,D=x+n+2,b=x+1;a.push(_,y,b),a.push(y,D,b)}}this.setIndex(a),this.setAttribute("position",new Ot(l,3)),this.setAttribute("normal",new Ot(c,3)),this.setAttribute("uv",new Ot(u,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new bu(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Au extends An{constructor(e=1,t=32,n=16,r=0,s=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:r,phiLength:s,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const l=Math.min(o+a,Math.PI);let c=0;const u=[],f=new k,d=new k,m=[],v=[],M=[],p=[];for(let h=0;h<=n;h++){const x=[],_=h/n;let y=0;h===0&&o===0?y=.5/t:h===n&&l===Math.PI&&(y=-.5/t);for(let D=0;D<=t;D++){const b=D/t;f.x=-e*Math.cos(r+b*s)*Math.sin(o+_*a),f.y=e*Math.cos(o+_*a),f.z=e*Math.sin(r+b*s)*Math.sin(o+_*a),v.push(f.x,f.y,f.z),d.copy(f).normalize(),M.push(d.x,d.y,d.z),p.push(b+y,1-_),x.push(c++)}u.push(x)}for(let h=0;h<n;h++)for(let x=0;x<t;x++){const _=u[h][x+1],y=u[h][x],D=u[h+1][x],b=u[h+1][x+1];(h!==0||o>0)&&m.push(_,y,b),(h!==n-1||l<Math.PI)&&m.push(y,D,b)}this.setIndex(m),this.setAttribute("position",new Ot(v,3)),this.setAttribute("normal",new Ot(M,3)),this.setAttribute("uv",new Ot(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Au(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}const qh={enabled:!1,files:{},add:function(i,e){this.enabled!==!1&&(this.files[i]=e)},get:function(i){if(this.enabled!==!1)return this.files[i]},remove:function(i){delete this.files[i]},clear:function(){this.files={}}};class lS{constructor(e,t,n){const r=this;let s=!1,o=0,a=0,l;const c=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(u){a++,s===!1&&r.onStart!==void 0&&r.onStart(u,o,a),s=!0},this.itemEnd=function(u){o++,r.onProgress!==void 0&&r.onProgress(u,o,a),o===a&&(s=!1,r.onLoad!==void 0&&r.onLoad())},this.itemError=function(u){r.onError!==void 0&&r.onError(u)},this.resolveURL=function(u){return l?l(u):u},this.setURLModifier=function(u){return l=u,this},this.addHandler=function(u,f){return c.push(u,f),this},this.removeHandler=function(u){const f=c.indexOf(u);return f!==-1&&c.splice(f,2),this},this.getHandler=function(u){for(let f=0,d=c.length;f<d;f+=2){const m=c[f],v=c[f+1];if(m.global&&(m.lastIndex=0),m.test(u))return v}return null}}}const cS=new lS;class wu{constructor(e){this.manager=e!==void 0?e:cS,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(r,s){n.load(e,r,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}wu.DEFAULT_MATERIAL_NAME="__DEFAULT";const Pi={};class uS extends Error{constructor(e,t){super(e),this.response=t}}class fS extends wu{constructor(e){super(e)}load(e,t,n,r){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=qh.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(Pi[e]!==void 0){Pi[e].push({onLoad:t,onProgress:n,onError:r});return}Pi[e]=[],Pi[e].push({onLoad:t,onProgress:n,onError:r});const o=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,l=this.responseType;fetch(o).then(c=>{if(c.status===200||c.status===0){if(c.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||c.body===void 0||c.body.getReader===void 0)return c;const u=Pi[e],f=c.body.getReader(),d=c.headers.get("Content-Length")||c.headers.get("X-File-Size"),m=d?parseInt(d):0,v=m!==0;let M=0;const p=new ReadableStream({start(h){x();function x(){f.read().then(({done:_,value:y})=>{if(_)h.close();else{M+=y.byteLength;const D=new ProgressEvent("progress",{lengthComputable:v,loaded:M,total:m});for(let b=0,R=u.length;b<R;b++){const q=u[b];q.onProgress&&q.onProgress(D)}h.enqueue(y),x()}})}}});return new Response(p)}else throw new uS(`fetch for "${c.url}" responded with ${c.status}: ${c.statusText}`,c)}).then(c=>{switch(l){case"arraybuffer":return c.arrayBuffer();case"blob":return c.blob();case"document":return c.text().then(u=>new DOMParser().parseFromString(u,a));case"json":return c.json();default:if(a===void 0)return c.text();{const f=/charset="?([^;"\s]*)"?/i.exec(a),d=f&&f[1]?f[1].toLowerCase():void 0,m=new TextDecoder(d);return c.arrayBuffer().then(v=>m.decode(v))}}}).then(c=>{qh.add(e,c);const u=Pi[e];delete Pi[e];for(let f=0,d=u.length;f<d;f++){const m=u[f];m.onLoad&&m.onLoad(c)}}).catch(c=>{const u=Pi[e];if(u===void 0)throw this.manager.itemError(e),c;delete Pi[e];for(let f=0,d=u.length;f<d;f++){const m=u[f];m.onError&&m.onError(c)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class Dp extends Zt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new ft(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),t}}const pc=new Bt,Yh=new k,jh=new k;class hS{constructor(e){this.camera=e,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new qe(512,512),this.map=null,this.mapPass=null,this.matrix=new Bt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Su,this._frameExtents=new qe(1,1),this._viewportCount=1,this._viewports=[new an(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Yh.setFromMatrixPosition(e.matrixWorld),t.position.copy(Yh),jh.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(jh),t.updateMatrixWorld(),pc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(pc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(pc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class dS extends hS{constructor(){super(new Mp(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class pS extends Dp{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Zt.DEFAULT_UP),this.updateMatrix(),this.target=new Zt,this.shadow=new dS}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class mS extends Dp{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class gS{constructor(e,t,n=0,r=1/0){this.ray=new Wo(e,t),this.near=n,this.far=r,this.camera=null,this.layers=new Mu,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}intersectObject(e,t=!0,n=[]){return su(e,this,n,t),n.sort($h),n}intersectObjects(e,t=!0,n=[]){for(let r=0,s=e.length;r<s;r++)su(e[r],this,n,t);return n.sort($h),n}}function $h(i,e){return i.distance-e.distance}function su(i,e,t,n){if(i.layers.test(e.layers)&&i.raycast(e,t),n===!0){const r=i.children;for(let s=0,o=r.length;s<o;s++)su(r[s],e,t,!0)}}class Kh{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(En(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}class _S extends oS{constructor(e=1){const t=[0,0,0,e,0,0,0,0,0,0,e,0,0,0,0,0,0,e],n=[1,0,0,1,.6,0,0,1,0,.6,1,0,0,0,1,0,.6,1],r=new An;r.setAttribute("position",new Ot(t,3)),r.setAttribute("color",new Ot(n,3));const s=new Lp({vertexColors:!0,toneMapped:!1});super(r,s),this.type="AxesHelper"}setColors(e,t,n){const r=new ft,s=this.geometry.attributes.color.array;return r.set(e),r.toArray(s,0),r.toArray(s,3),r.set(t),r.toArray(s,6),r.toArray(s,9),r.set(n),r.toArray(s,12),r.toArray(s,15),this.geometry.attributes.color.needsUpdate=!0,this}dispose(){this.geometry.dispose(),this.material.dispose()}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:_u}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=_u);const Zh={type:"change"},mc={type:"start"},Jh={type:"end"},Pa=new Wo,Qh=new ir,vS=Math.cos(70*$g.DEG2RAD);class xS extends jr{constructor(e,t){super(),this.object=e,this.domElement=t,this.domElement.style.touchAction="none",this.enabled=!0,this.target=new k,this.cursor=new k,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:ls.ROTATE,MIDDLE:ls.DOLLY,RIGHT:ls.PAN},this.touches={ONE:cs.ROTATE,TWO:cs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this.getPolarAngle=function(){return a.phi},this.getAzimuthalAngle=function(){return a.theta},this.getDistance=function(){return this.object.position.distanceTo(this.target)},this.listenToKeyEvents=function(U){U.addEventListener("keydown",Fe),this._domElementKeyEvents=U},this.stopListenToKeyEvents=function(){this._domElementKeyEvents.removeEventListener("keydown",Fe),this._domElementKeyEvents=null},this.saveState=function(){n.target0.copy(n.target),n.position0.copy(n.object.position),n.zoom0=n.object.zoom},this.reset=function(){n.target.copy(n.target0),n.object.position.copy(n.position0),n.object.zoom=n.zoom0,n.object.updateProjectionMatrix(),n.dispatchEvent(Zh),n.update(),s=r.NONE},this.update=function(){const U=new k,pe=new _r().setFromUnitVectors(e.up,new k(0,1,0)),De=pe.clone().invert(),Ae=new k,he=new _r,F=new k,me=2*Math.PI;return function(Xe=null){const He=n.object.position;U.copy(He).sub(n.target),U.applyQuaternion(pe),a.setFromVector3(U),n.autoRotate&&s===r.NONE&&Y(A(Xe)),n.enableDamping?(a.theta+=l.theta*n.dampingFactor,a.phi+=l.phi*n.dampingFactor):(a.theta+=l.theta,a.phi+=l.phi);let st=n.minAzimuthAngle,ot=n.maxAzimuthAngle;isFinite(st)&&isFinite(ot)&&(st<-Math.PI?st+=me:st>Math.PI&&(st-=me),ot<-Math.PI?ot+=me:ot>Math.PI&&(ot-=me),st<=ot?a.theta=Math.max(st,Math.min(ot,a.theta)):a.theta=a.theta>(st+ot)/2?Math.max(st,a.theta):Math.min(ot,a.theta)),a.phi=Math.max(n.minPolarAngle,Math.min(n.maxPolarAngle,a.phi)),a.makeSafe(),n.enableDamping===!0?n.target.addScaledVector(u,n.dampingFactor):n.target.add(u),n.target.sub(n.cursor),n.target.clampLength(n.minTargetRadius,n.maxTargetRadius),n.target.add(n.cursor),n.zoomToCursor&&b||n.object.isOrthographicCamera?a.radius=Q(a.radius):a.radius=Q(a.radius*c),U.setFromSpherical(a),U.applyQuaternion(De),He.copy(n.target).add(U),n.object.lookAt(n.target),n.enableDamping===!0?(l.theta*=1-n.dampingFactor,l.phi*=1-n.dampingFactor,u.multiplyScalar(1-n.dampingFactor)):(l.set(0,0,0),u.set(0,0,0));let Nt=!1;if(n.zoomToCursor&&b){let St=null;if(n.object.isPerspectiveCamera){const je=U.length();St=Q(je*c);const gt=je-St;n.object.position.addScaledVector(y,gt),n.object.updateMatrixWorld()}else if(n.object.isOrthographicCamera){const je=new k(D.x,D.y,0);je.unproject(n.object),n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/c)),n.object.updateProjectionMatrix(),Nt=!0;const gt=new k(D.x,D.y,0);gt.unproject(n.object),n.object.position.sub(gt).add(je),n.object.updateMatrixWorld(),St=U.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),n.zoomToCursor=!1;St!==null&&(this.screenSpacePanning?n.target.set(0,0,-1).transformDirection(n.object.matrix).multiplyScalar(St).add(n.object.position):(Pa.origin.copy(n.object.position),Pa.direction.set(0,0,-1).transformDirection(n.object.matrix),Math.abs(n.object.up.dot(Pa.direction))<vS?e.lookAt(n.target):(Qh.setFromNormalAndCoplanarPoint(n.object.up,n.target),Pa.intersectPlane(Qh,n.target))))}else n.object.isOrthographicCamera&&(n.object.zoom=Math.max(n.minZoom,Math.min(n.maxZoom,n.object.zoom/c)),n.object.updateProjectionMatrix(),Nt=!0);return c=1,b=!1,Nt||Ae.distanceToSquared(n.object.position)>o||8*(1-he.dot(n.object.quaternion))>o||F.distanceToSquared(n.target)>0?(n.dispatchEvent(Zh),Ae.copy(n.object.position),he.copy(n.object.quaternion),F.copy(n.target),!0):!1}}(),this.dispose=function(){n.domElement.removeEventListener("contextmenu",rt),n.domElement.removeEventListener("pointerdown",L),n.domElement.removeEventListener("pointercancel",$),n.domElement.removeEventListener("wheel",ee),n.domElement.removeEventListener("pointermove",E),n.domElement.removeEventListener("pointerup",$),n._domElementKeyEvents!==null&&(n._domElementKeyEvents.removeEventListener("keydown",Fe),n._domElementKeyEvents=null)};const n=this,r={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6};let s=r.NONE;const o=1e-6,a=new Kh,l=new Kh;let c=1;const u=new k,f=new qe,d=new qe,m=new qe,v=new qe,M=new qe,p=new qe,h=new qe,x=new qe,_=new qe,y=new k,D=new qe;let b=!1;const R=[],q={};let T=!1;function A(U){return U!==null?2*Math.PI/60*n.autoRotateSpeed*U:2*Math.PI/60/60*n.autoRotateSpeed}function I(U){const pe=Math.abs(U*.01);return Math.pow(.95,n.zoomSpeed*pe)}function Y(U){l.theta-=U}function J(U){l.phi-=U}const N=function(){const U=new k;return function(De,Ae){U.setFromMatrixColumn(Ae,0),U.multiplyScalar(-De),u.add(U)}}(),B=function(){const U=new k;return function(De,Ae){n.screenSpacePanning===!0?U.setFromMatrixColumn(Ae,1):(U.setFromMatrixColumn(Ae,0),U.crossVectors(n.object.up,U)),U.multiplyScalar(De),u.add(U)}}(),V=function(){const U=new k;return function(De,Ae){const he=n.domElement;if(n.object.isPerspectiveCamera){const F=n.object.position;U.copy(F).sub(n.target);let me=U.length();me*=Math.tan(n.object.fov/2*Math.PI/180),N(2*De*me/he.clientHeight,n.object.matrix),B(2*Ae*me/he.clientHeight,n.object.matrix)}else n.object.isOrthographicCamera?(N(De*(n.object.right-n.object.left)/n.object.zoom/he.clientWidth,n.object.matrix),B(Ae*(n.object.top-n.object.bottom)/n.object.zoom/he.clientHeight,n.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),n.enablePan=!1)}}();function W(U){n.object.isPerspectiveCamera||n.object.isOrthographicCamera?c/=U:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function ie(U){n.object.isPerspectiveCamera||n.object.isOrthographicCamera?c*=U:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),n.enableZoom=!1)}function te(U,pe){if(!n.zoomToCursor)return;b=!0;const De=n.domElement.getBoundingClientRect(),Ae=U-De.left,he=pe-De.top,F=De.width,me=De.height;D.x=Ae/F*2-1,D.y=-(he/me)*2+1,y.set(D.x,D.y,1).unproject(n.object).sub(n.object.position).normalize()}function Q(U){return Math.max(n.minDistance,Math.min(n.maxDistance,U))}function ae(U){f.set(U.clientX,U.clientY)}function re(U){te(U.clientX,U.clientX),h.set(U.clientX,U.clientY)}function z(U){v.set(U.clientX,U.clientY)}function se(U){d.set(U.clientX,U.clientY),m.subVectors(d,f).multiplyScalar(n.rotateSpeed);const pe=n.domElement;Y(2*Math.PI*m.x/pe.clientHeight),J(2*Math.PI*m.y/pe.clientHeight),f.copy(d),n.update()}function ve(U){x.set(U.clientX,U.clientY),_.subVectors(x,h),_.y>0?W(I(_.y)):_.y<0&&ie(I(_.y)),h.copy(x),n.update()}function Se(U){M.set(U.clientX,U.clientY),p.subVectors(M,v).multiplyScalar(n.panSpeed),V(p.x,p.y),v.copy(M),n.update()}function ge(U){te(U.clientX,U.clientY),U.deltaY<0?ie(I(U.deltaY)):U.deltaY>0&&W(I(U.deltaY)),n.update()}function ke(U){let pe=!1;switch(U.code){case n.keys.UP:U.ctrlKey||U.metaKey||U.shiftKey?J(2*Math.PI*n.rotateSpeed/n.domElement.clientHeight):V(0,n.keyPanSpeed),pe=!0;break;case n.keys.BOTTOM:U.ctrlKey||U.metaKey||U.shiftKey?J(-2*Math.PI*n.rotateSpeed/n.domElement.clientHeight):V(0,-n.keyPanSpeed),pe=!0;break;case n.keys.LEFT:U.ctrlKey||U.metaKey||U.shiftKey?Y(2*Math.PI*n.rotateSpeed/n.domElement.clientHeight):V(n.keyPanSpeed,0),pe=!0;break;case n.keys.RIGHT:U.ctrlKey||U.metaKey||U.shiftKey?Y(-2*Math.PI*n.rotateSpeed/n.domElement.clientHeight):V(-n.keyPanSpeed,0),pe=!0;break}pe&&(U.preventDefault(),n.update())}function Be(U){if(R.length===1)f.set(U.pageX,U.pageY);else{const pe=ye(U),De=.5*(U.pageX+pe.x),Ae=.5*(U.pageY+pe.y);f.set(De,Ae)}}function be(U){if(R.length===1)v.set(U.pageX,U.pageY);else{const pe=ye(U),De=.5*(U.pageX+pe.x),Ae=.5*(U.pageY+pe.y);v.set(De,Ae)}}function Ke(U){const pe=ye(U),De=U.pageX-pe.x,Ae=U.pageY-pe.y,he=Math.sqrt(De*De+Ae*Ae);h.set(0,he)}function j(U){n.enableZoom&&Ke(U),n.enablePan&&be(U)}function xt(U){n.enableZoom&&Ke(U),n.enableRotate&&Be(U)}function Ue(U){if(R.length==1)d.set(U.pageX,U.pageY);else{const De=ye(U),Ae=.5*(U.pageX+De.x),he=.5*(U.pageY+De.y);d.set(Ae,he)}m.subVectors(d,f).multiplyScalar(n.rotateSpeed);const pe=n.domElement;Y(2*Math.PI*m.x/pe.clientHeight),J(2*Math.PI*m.y/pe.clientHeight),f.copy(d)}function Ve(U){if(R.length===1)M.set(U.pageX,U.pageY);else{const pe=ye(U),De=.5*(U.pageX+pe.x),Ae=.5*(U.pageY+pe.y);M.set(De,Ae)}p.subVectors(M,v).multiplyScalar(n.panSpeed),V(p.x,p.y),v.copy(M)}function Le(U){const pe=ye(U),De=U.pageX-pe.x,Ae=U.pageY-pe.y,he=Math.sqrt(De*De+Ae*Ae);x.set(0,he),_.set(0,Math.pow(x.y/h.y,n.zoomSpeed)),W(_.y),h.copy(x);const F=(U.pageX+pe.x)*.5,me=(U.pageY+pe.y)*.5;te(F,me)}function mt(U){n.enableZoom&&Le(U),n.enablePan&&Ve(U)}function Ze(U){n.enableZoom&&Le(U),n.enableRotate&&Ue(U)}function L(U){n.enabled!==!1&&(R.length===0&&(n.domElement.setPointerCapture(U.pointerId),n.domElement.addEventListener("pointermove",E),n.domElement.addEventListener("pointerup",$)),Ge(U),U.pointerType==="touch"?Ye(U):ue(U))}function E(U){n.enabled!==!1&&(U.pointerType==="touch"?le(U):ce(U))}function $(U){Oe(U),R.length===0&&(n.domElement.releasePointerCapture(U.pointerId),n.domElement.removeEventListener("pointermove",E),n.domElement.removeEventListener("pointerup",$)),n.dispatchEvent(Jh),s=r.NONE}function ue(U){let pe;switch(U.button){case 0:pe=n.mouseButtons.LEFT;break;case 1:pe=n.mouseButtons.MIDDLE;break;case 2:pe=n.mouseButtons.RIGHT;break;default:pe=-1}switch(pe){case ls.DOLLY:if(n.enableZoom===!1)return;re(U),s=r.DOLLY;break;case ls.ROTATE:if(U.ctrlKey||U.metaKey||U.shiftKey){if(n.enablePan===!1)return;z(U),s=r.PAN}else{if(n.enableRotate===!1)return;ae(U),s=r.ROTATE}break;case ls.PAN:if(U.ctrlKey||U.metaKey||U.shiftKey){if(n.enableRotate===!1)return;ae(U),s=r.ROTATE}else{if(n.enablePan===!1)return;z(U),s=r.PAN}break;default:s=r.NONE}s!==r.NONE&&n.dispatchEvent(mc)}function ce(U){switch(s){case r.ROTATE:if(n.enableRotate===!1)return;se(U);break;case r.DOLLY:if(n.enableZoom===!1)return;ve(U);break;case r.PAN:if(n.enablePan===!1)return;Se(U);break}}function ee(U){n.enabled===!1||n.enableZoom===!1||s!==r.NONE||(U.preventDefault(),n.dispatchEvent(mc),ge(ne(U)),n.dispatchEvent(Jh))}function ne(U){const pe=U.deltaMode,De={clientX:U.clientX,clientY:U.clientY,deltaY:U.deltaY};switch(pe){case 1:De.deltaY*=16;break;case 2:De.deltaY*=100;break}return U.ctrlKey&&!T&&(De.deltaY*=10),De}function fe(U){U.key==="Control"&&(T=!0,document.addEventListener("keyup",Me,{passive:!0,capture:!0}))}function Me(U){U.key==="Control"&&(T=!1,document.removeEventListener("keyup",Me,{passive:!0,capture:!0}))}function Fe(U){n.enabled===!1||n.enablePan===!1||ke(U)}function Ye(U){switch(Ce(U),R.length){case 1:switch(n.touches.ONE){case cs.ROTATE:if(n.enableRotate===!1)return;Be(U),s=r.TOUCH_ROTATE;break;case cs.PAN:if(n.enablePan===!1)return;be(U),s=r.TOUCH_PAN;break;default:s=r.NONE}break;case 2:switch(n.touches.TWO){case cs.DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;j(U),s=r.TOUCH_DOLLY_PAN;break;case cs.DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;xt(U),s=r.TOUCH_DOLLY_ROTATE;break;default:s=r.NONE}break;default:s=r.NONE}s!==r.NONE&&n.dispatchEvent(mc)}function le(U){switch(Ce(U),s){case r.TOUCH_ROTATE:if(n.enableRotate===!1)return;Ue(U),n.update();break;case r.TOUCH_PAN:if(n.enablePan===!1)return;Ve(U),n.update();break;case r.TOUCH_DOLLY_PAN:if(n.enableZoom===!1&&n.enablePan===!1)return;mt(U),n.update();break;case r.TOUCH_DOLLY_ROTATE:if(n.enableZoom===!1&&n.enableRotate===!1)return;Ze(U),n.update();break;default:s=r.NONE}}function rt(U){n.enabled!==!1&&U.preventDefault()}function Ge(U){R.push(U.pointerId)}function Oe(U){delete q[U.pointerId];for(let pe=0;pe<R.length;pe++)if(R[pe]==U.pointerId){R.splice(pe,1);return}}function Ce(U){let pe=q[U.pointerId];pe===void 0&&(pe=new qe,q[U.pointerId]=pe),pe.set(U.pageX,U.pageY)}function ye(U){const pe=U.pointerId===R[0]?R[1]:R[0];return q[pe]}n.domElement.addEventListener("contextmenu",rt),n.domElement.addEventListener("pointerdown",L),n.domElement.addEventListener("pointercancel",$),n.domElement.addEventListener("wheel",ee,{passive:!1}),document.addEventListener("keydown",fe,{passive:!0,capture:!0}),this.update()}}const Cn=new ft;class MS extends wu{constructor(e){super(e),this.propertyNameMapping={},this.customPropertyMapping={}}load(e,t,n,r){const s=this,o=new fS(this.manager);o.setPath(this.path),o.setResponseType("arraybuffer"),o.setRequestHeader(this.requestHeader),o.setWithCredentials(this.withCredentials),o.load(e,function(a){try{t(s.parse(a))}catch(l){r?r(l):console.error(l),s.manager.itemError(e)}},n,r)}setPropertyNameMapping(e){this.propertyNameMapping=e}setCustomPropertyNameMapping(e){this.customPropertyMapping=e}parse(e){function t(p,h=0){const x=/^ply([\s\S]*)end_header(\r\n|\r|\n)/;let _="";const y=x.exec(p);y!==null&&(_=y[1]);const D={comments:[],elements:[],headerLength:h,objInfo:""},b=_.split(/\r\n|\r|\n/);let R;function q(T,A){const I={type:T[0]};return I.type==="list"?(I.name=T[3],I.countType=T[1],I.itemType=T[2]):I.name=T[1],I.name in A&&(I.name=A[I.name]),I}for(let T=0;T<b.length;T++){let A=b[T];if(A=A.trim(),A==="")continue;const I=A.split(/\s+/),Y=I.shift();switch(A=I.join(" "),Y){case"format":D.format=I[0],D.version=I[1];break;case"comment":D.comments.push(A);break;case"element":R!==void 0&&D.elements.push(R),R={},R.name=I[0],R.count=parseInt(I[1]),R.properties=[];break;case"property":R.properties.push(q(I,M.propertyNameMapping));break;case"obj_info":D.objInfo=A;break;default:console.log("unhandled",Y,I)}}return R!==void 0&&D.elements.push(R),D}function n(p,h){switch(h){case"char":case"uchar":case"short":case"ushort":case"int":case"uint":case"int8":case"uint8":case"int16":case"uint16":case"int32":case"uint32":return parseInt(p);case"float":case"double":case"float32":case"float64":return parseFloat(p)}}function r(p,h){const x={};for(let _=0;_<p.length;_++){if(h.empty())return null;if(p[_].type==="list"){const y=[],D=n(h.next(),p[_].countType);for(let b=0;b<D;b++){if(h.empty())return null;y.push(n(h.next(),p[_].itemType))}x[p[_].name]=y}else x[p[_].name]=n(h.next(),p[_].type)}return x}function s(){const p={indices:[],vertices:[],normals:[],uvs:[],faceVertexUvs:[],colors:[],faceVertexColors:[]};for(const h of Object.keys(M.customPropertyMapping))p[h]=[];return p}function o(p){const h=p.map(_=>_.name);function x(_){for(let y=0,D=_.length;y<D;y++){const b=_[y];if(h.includes(b))return b}return null}return{attrX:x(["x","px","posx"])||"x",attrY:x(["y","py","posy"])||"y",attrZ:x(["z","pz","posz"])||"z",attrNX:x(["nx","normalx"]),attrNY:x(["ny","normaly"]),attrNZ:x(["nz","normalz"]),attrS:x(["s","u","texture_u","tx"]),attrT:x(["t","v","texture_v","ty"]),attrR:x(["red","diffuse_red","r","diffuse_r"]),attrG:x(["green","diffuse_green","g","diffuse_g"]),attrB:x(["blue","diffuse_blue","b","diffuse_b"])}}function a(p,h){const x=s(),_=/end_header\s+(\S[\s\S]*\S|\S)\s*$/;let y,D;(D=_.exec(p))!==null?y=D[1].split(/\s+/):y=[];const b=new SS(y);e:for(let R=0;R<h.elements.length;R++){const q=h.elements[R],T=o(q.properties);for(let A=0;A<q.count;A++){const I=r(q.properties,b);if(!I)break e;c(x,q.name,I,T)}}return l(x)}function l(p){let h=new An;p.indices.length>0&&h.setIndex(p.indices),h.setAttribute("position",new Ot(p.vertices,3)),p.normals.length>0&&h.setAttribute("normal",new Ot(p.normals,3)),p.uvs.length>0&&h.setAttribute("uv",new Ot(p.uvs,2)),p.colors.length>0&&h.setAttribute("color",new Ot(p.colors,3)),(p.faceVertexUvs.length>0||p.faceVertexColors.length>0)&&(h=h.toNonIndexed(),p.faceVertexUvs.length>0&&h.setAttribute("uv",new Ot(p.faceVertexUvs,2)),p.faceVertexColors.length>0&&h.setAttribute("color",new Ot(p.faceVertexColors,3)));for(const x of Object.keys(M.customPropertyMapping))p[x].length>0&&h.setAttribute(x,new Ot(p[x],M.customPropertyMapping[x].length));return h.computeBoundingSphere(),h}function c(p,h,x,_){if(h==="vertex"){p.vertices.push(x[_.attrX],x[_.attrY],x[_.attrZ]),_.attrNX!==null&&_.attrNY!==null&&_.attrNZ!==null&&p.normals.push(x[_.attrNX],x[_.attrNY],x[_.attrNZ]),_.attrS!==null&&_.attrT!==null&&p.uvs.push(x[_.attrS],x[_.attrT]),_.attrR!==null&&_.attrG!==null&&_.attrB!==null&&(Cn.setRGB(x[_.attrR]/255,x[_.attrG]/255,x[_.attrB]/255).convertSRGBToLinear(),p.colors.push(Cn.r,Cn.g,Cn.b));for(const y of Object.keys(M.customPropertyMapping))for(const D of M.customPropertyMapping[y])p[y].push(x[D])}else if(h==="face"){const y=x.vertex_indices||x.vertex_index,D=x.texcoord;y.length===3?(p.indices.push(y[0],y[1],y[2]),D&&D.length===6&&(p.faceVertexUvs.push(D[0],D[1]),p.faceVertexUvs.push(D[2],D[3]),p.faceVertexUvs.push(D[4],D[5]))):y.length===4&&(p.indices.push(y[0],y[1],y[3]),p.indices.push(y[1],y[2],y[3])),_.attrR!==null&&_.attrG!==null&&_.attrB!==null&&(Cn.setRGB(x[_.attrR]/255,x[_.attrG]/255,x[_.attrB]/255).convertSRGBToLinear(),p.faceVertexColors.push(Cn.r,Cn.g,Cn.b),p.faceVertexColors.push(Cn.r,Cn.g,Cn.b),p.faceVertexColors.push(Cn.r,Cn.g,Cn.b))}}function u(p,h){const x={};let _=0;for(let y=0;y<h.length;y++){const D=h[y],b=D.valueReader;if(D.type==="list"){const R=[],q=D.countReader.read(p+_);_+=D.countReader.size;for(let T=0;T<q;T++)R.push(b.read(p+_)),_+=b.size;x[D.name]=R}else x[D.name]=b.read(p+_),_+=b.size}return[x,_]}function f(p,h,x){function _(y,D,b){switch(D){case"int8":case"char":return{read:R=>y.getInt8(R),size:1};case"uint8":case"uchar":return{read:R=>y.getUint8(R),size:1};case"int16":case"short":return{read:R=>y.getInt16(R,b),size:2};case"uint16":case"ushort":return{read:R=>y.getUint16(R,b),size:2};case"int32":case"int":return{read:R=>y.getInt32(R,b),size:4};case"uint32":case"uint":return{read:R=>y.getUint32(R,b),size:4};case"float32":case"float":return{read:R=>y.getFloat32(R,b),size:4};case"float64":case"double":return{read:R=>y.getFloat64(R,b),size:8}}}for(let y=0,D=p.length;y<D;y++){const b=p[y];b.type==="list"?(b.countReader=_(h,b.countType,x),b.valueReader=_(h,b.itemType,x)):b.valueReader=_(h,b.type,x)}}function d(p,h){const x=s(),_=h.format==="binary_little_endian",y=new DataView(p,h.headerLength);let D,b=0;for(let R=0;R<h.elements.length;R++){const q=h.elements[R],T=q.properties,A=o(T);f(T,y,_);for(let I=0;I<q.count;I++){D=u(b,T),b+=D[1];const Y=D[0];c(x,q.name,Y,A)}}return l(x)}function m(p){let h=0,x=!0,_="";const y=[],D=new TextDecoder().decode(p.subarray(0,5)),b=/^ply\r\n/.test(D);do{const R=String.fromCharCode(p[h++]);R!==`
`&&R!=="\r"?_+=R:(_==="end_header"&&(x=!1),_!==""&&(y.push(_),_=""))}while(x&&h<p.length);return b===!0&&h++,{headerText:y.join("\r")+"\r",headerLength:h}}let v;const M=this;if(e instanceof ArrayBuffer){const p=new Uint8Array(e),{headerText:h,headerLength:x}=m(p),_=t(h,x);if(_.format==="ascii"){const y=new TextDecoder().decode(p);v=a(y,_)}else v=d(e,_)}else v=a(e,t(e));return v}}class SS{constructor(e){this.arr=e,this.i=0}empty(){return this.i>=this.arr.length}next(){return this.arr[this.i++]}}const yS=!0,en="u-",ES="uplot",TS=en+"hz",bS=en+"vt",AS=en+"title",wS=en+"wrap",RS=en+"under",CS=en+"over",LS=en+"axis",Br=en+"off",PS=en+"select",DS=en+"cursor-x",US=en+"cursor-y",IS=en+"cursor-pt",NS=en+"legend",FS=en+"live",OS=en+"inline",BS=en+"series",zS=en+"marker",ed=en+"label",kS=en+"value",bo="width",Ao="height",_o="top",td="bottom",Ls="left",gc="right",Ru="#000",nd=Ru+"0",_c="mousemove",id="mousedown",vc="mouseup",rd="mouseenter",sd="mouseleave",od="dblclick",HS="resize",GS="scroll",ad="change",Qa="dppxchange",Cu="--",Js=typeof window<"u",ou=Js?document:null,Bs=Js?window:null,VS=Js?navigator:null;let vt,Da;function au(){let i=devicePixelRatio;vt!=i&&(vt=i,Da&&cu(ad,Da,au),Da=matchMedia(`(min-resolution: ${vt-.001}dppx) and (max-resolution: ${vt+.001}dppx)`),Vr(ad,Da,au),Bs.dispatchEvent(new CustomEvent(Qa)))}function zn(i,e){if(e!=null){let t=i.classList;!t.contains(e)&&t.add(e)}}function lu(i,e){let t=i.classList;t.contains(e)&&t.remove(e)}function Ut(i,e,t){i.style[e]=t+"px"}function li(i,e,t,n){let r=ou.createElement(i);return e!=null&&zn(r,e),t!=null&&t.insertBefore(r,n),r}function jn(i,e){return li("div",i,e)}const ld=new WeakMap;function _i(i,e,t,n,r){let s="translate("+e+"px,"+t+"px)",o=ld.get(i);s!=o&&(i.style.transform=s,ld.set(i,s),e<0||t<0||e>n||t>r?zn(i,Br):lu(i,Br))}const cd=new WeakMap;function ud(i,e,t){let n=e+t,r=cd.get(i);n!=r&&(cd.set(i,n),i.style.background=e,i.style.borderColor=t)}const fd=new WeakMap;function hd(i,e,t,n){let r=e+""+t,s=fd.get(i);r!=s&&(fd.set(i,r),i.style.height=t+"px",i.style.width=e+"px",i.style.marginLeft=n?-e/2+"px":0,i.style.marginTop=n?-t/2+"px":0)}const Lu={passive:!0},WS={...Lu,capture:!0};function Vr(i,e,t,n){e.addEventListener(i,t,n?WS:Lu)}function cu(i,e,t,n){e.removeEventListener(i,t,Lu)}Js&&au();function ci(i,e,t,n){let r;t=t||0,n=n||e.length-1;let s=n<=2147483647;for(;n-t>1;)r=s?t+n>>1:Vn((t+n)/2),e[r]<i?t=r:n=r;return i-e[t]<=e[n]-i?t:n}function Up(i){return(t,n,r)=>{let s=-1,o=-1;for(let a=n;a<=r;a++)if(i(t[a])){s=a;break}for(let a=r;a>=n;a--)if(i(t[a])){o=a;break}return[s,o]}}const Ip=i=>i!=null,Np=i=>i!=null&&i>0,hl=Up(Ip),XS=Up(Np);function qS(i,e,t,n=0,r=!1){let s=r?XS:hl,o=r?Np:Ip;[e,t]=s(i,e,t);let a=i[e],l=i[e];if(e>-1)if(n==1)a=i[e],l=i[t];else if(n==-1)a=i[t],l=i[e];else for(let c=e;c<=t;c++){let u=i[c];o(u)&&(u<a?a=u:u>l&&(l=u))}return[a??wt,l??-wt]}function dl(i,e,t,n){let r=md(i),s=md(e);i==e&&(r==-1?(i*=t,e/=t):(i/=t,e*=t));let o=t==10?Hi:Fp,a=r==1?Vn:$n,l=s==1?$n:Vn,c=a(o($t(i))),u=l(o($t(e))),f=Ws(t,c),d=Ws(t,u);return t==10&&(c<0&&(f=Rt(f,-c)),u<0&&(d=Rt(d,-u))),n||t==2?(i=f*r,e=d*s):(i=kp(i,f),e=pl(e,d)),[i,e]}function Pu(i,e,t,n){let r=dl(i,e,t,n);return i==0&&(r[0]=0),e==0&&(r[1]=0),r}const Du=.1,dd={mode:3,pad:Du},Po={pad:0,soft:null,mode:0},YS={min:Po,max:Po};function el(i,e,t,n){return ml(t)?pd(i,e,t):(Po.pad=t,Po.soft=n?0:null,Po.mode=n?3:0,pd(i,e,YS))}function dt(i,e){return i??e}function jS(i,e,t){for(e=dt(e,0),t=dt(t,i.length-1);e<=t;){if(i[e]!=null)return!0;e++}return!1}function pd(i,e,t){let n=t.min,r=t.max,s=dt(n.pad,0),o=dt(r.pad,0),a=dt(n.hard,-wt),l=dt(r.hard,wt),c=dt(n.soft,wt),u=dt(r.soft,-wt),f=dt(n.mode,0),d=dt(r.mode,0),m=e-i,v=Hi(m),M=Tn($t(i),$t(e)),p=Hi(M),h=$t(p-v);(m<1e-24||h>10)&&(m=0,(i==0||e==0)&&(m=1e-24,f==2&&c!=wt&&(s=0),d==2&&u!=-wt&&(o=0)));let x=m||M||1e3,_=Hi(x),y=Ws(10,Vn(_)),D=x*(m==0?i==0?.1:1:s),b=Rt(kp(i-D,y/10),24),R=i>=c&&(f==1||f==3&&b<=c||f==2&&b>=c)?c:wt,q=Tn(a,b<R&&i>=R?R:hi(R,b)),T=x*(m==0?e==0?.1:1:o),A=Rt(pl(e+T,y/10),24),I=e<=u&&(d==1||d==3&&A>=u||d==2&&A<=u)?u:-wt,Y=hi(l,A>I&&e<=I?I:Tn(I,A));return q==Y&&q==0&&(Y=100),[q,Y]}const $S=new Intl.NumberFormat(Js?VS.language:"en-US"),Uu=i=>$S.format(i),Wn=Math,Wa=Wn.PI,$t=Wn.abs,Vn=Wn.floor,jt=Wn.round,$n=Wn.ceil,hi=Wn.min,Tn=Wn.max,Ws=Wn.pow,md=Wn.sign,Hi=Wn.log10,Fp=Wn.log2,KS=(i,e=1)=>Wn.sinh(i)*e,xc=(i,e=1)=>Wn.asinh(i/e),wt=1/0;function gd(i){return(Hi((i^i>>31)-(i>>31))|0)+1}function uu(i,e,t){return hi(Tn(i,e),t)}function Op(i){return typeof i=="function"}function ut(i){return Op(i)?i:()=>i}const ZS=()=>{},Bp=i=>i,zp=(i,e)=>e,JS=i=>null,_d=i=>!0,vd=(i,e)=>i==e,QS=/\.\d*?(?=9{6,}|0{6,})/gm,Yr=i=>{if(Gp(i)||vr.has(i))return i;const e=`${i}`,t=e.match(QS);if(t==null)return i;let n=t[0].length-1;if(e.indexOf("e-")!=-1){let[r,s]=e.split("e");return+`${Yr(r)}e${s}`}return Rt(i,n)};function Ir(i,e){return Yr(Rt(Yr(i/e))*e)}function pl(i,e){return Yr($n(Yr(i/e))*e)}function kp(i,e){return Yr(Vn(Yr(i/e))*e)}function Rt(i,e=0){if(Gp(i))return i;let t=10**e,n=i*t*(1+Number.EPSILON);return jt(n)/t}const vr=new Map;function Hp(i){return((""+i).split(".")[1]||"").length}function Oo(i,e,t,n){let r=[],s=n.map(Hp);for(let o=e;o<t;o++){let a=$t(o),l=Rt(Ws(i,o),a);for(let c=0;c<n.length;c++){let u=i==10?+`${n[c]}e${o}`:n[c]*l,f=(o>=0?0:a)+(o>=s[c]?0:s[c]),d=i==10?u:Rt(u,f);r.push(d),vr.set(d,f)}}return r}const Do={},Iu=[],Xs=[null,null],rr=Array.isArray,Gp=Number.isInteger,ey=i=>i===void 0;function xd(i){return typeof i=="string"}function ml(i){let e=!1;if(i!=null){let t=i.constructor;e=t==null||t==Object}return e}function ty(i){return i!=null&&typeof i=="object"}const ny=Object.getPrototypeOf(Uint8Array),Vp="__proto__";function qs(i,e=ml){let t;if(rr(i)){let n=i.find(r=>r!=null);if(rr(n)||e(n)){t=Array(i.length);for(let r=0;r<i.length;r++)t[r]=qs(i[r],e)}else t=i.slice()}else if(i instanceof ny)t=i.slice();else if(e(i)){t={};for(let n in i)n!=Vp&&(t[n]=qs(i[n],e))}else t=i;return t}function qt(i){let e=arguments;for(let t=1;t<e.length;t++){let n=e[t];for(let r in n)r!=Vp&&(ml(i[r])?qt(i[r],qs(n[r])):i[r]=qs(n[r]))}return i}const iy=0,ry=1,sy=2;function oy(i,e,t){for(let n=0,r,s=-1;n<e.length;n++){let o=e[n];if(o>s){for(r=o-1;r>=0&&i[r]==null;)i[r--]=null;for(r=o+1;r<t&&i[r]==null;)i[s=r++]=null}}}function ay(i,e){if(uy(i)){let o=i[0].slice();for(let a=1;a<i.length;a++)o.push(...i[a].slice(1));return fy(o[0])||(o=cy(o)),o}let t=new Set;for(let o=0;o<i.length;o++){let l=i[o][0],c=l.length;for(let u=0;u<c;u++)t.add(l[u])}let n=[Array.from(t).sort((o,a)=>o-a)],r=n[0].length,s=new Map;for(let o=0;o<r;o++)s.set(n[0][o],o);for(let o=0;o<i.length;o++){let a=i[o],l=a[0];for(let c=1;c<a.length;c++){let u=a[c],f=Array(r).fill(void 0),d=e?e[o][c]:ry,m=[];for(let v=0;v<u.length;v++){let M=u[v],p=s.get(l[v]);M===null?d!=iy&&(f[p]=M,d==sy&&m.push(p)):f[p]=M}oy(f,m,r),n.push(f)}}return n}const ly=typeof queueMicrotask>"u"?i=>Promise.resolve().then(i):queueMicrotask;function cy(i){let e=i[0],t=e.length,n=Array(t);for(let s=0;s<n.length;s++)n[s]=s;n.sort((s,o)=>e[s]-e[o]);let r=[];for(let s=0;s<i.length;s++){let o=i[s],a=Array(t);for(let l=0;l<t;l++)a[l]=o[n[l]];r.push(a)}return r}function uy(i){let e=i[0][0],t=e.length;for(let n=1;n<i.length;n++){let r=i[n][0];if(r.length!=t)return!1;if(r!=e){for(let s=0;s<t;s++)if(r[s]!=e[s])return!1}}return!0}function fy(i,e=100){const t=i.length;if(t<=1)return!0;let n=0,r=t-1;for(;n<=r&&i[n]==null;)n++;for(;r>=n&&i[r]==null;)r--;if(r<=n)return!0;const s=Tn(1,Vn((r-n+1)/e));for(let o=i[n],a=n+s;a<=r;a+=s){const l=i[a];if(l!=null){if(l<=o)return!1;o=l}}return!0}const Wp=["January","February","March","April","May","June","July","August","September","October","November","December"],Xp=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function qp(i){return i.slice(0,3)}const hy=Xp.map(qp),dy=Wp.map(qp),py={MMMM:Wp,MMM:dy,WWWW:Xp,WWW:hy};function vo(i){return(i<10?"0":"")+i}function my(i){return(i<10?"00":i<100?"0":"")+i}const gy={YYYY:i=>i.getFullYear(),YY:i=>(i.getFullYear()+"").slice(2),MMMM:(i,e)=>e.MMMM[i.getMonth()],MMM:(i,e)=>e.MMM[i.getMonth()],MM:i=>vo(i.getMonth()+1),M:i=>i.getMonth()+1,DD:i=>vo(i.getDate()),D:i=>i.getDate(),WWWW:(i,e)=>e.WWWW[i.getDay()],WWW:(i,e)=>e.WWW[i.getDay()],HH:i=>vo(i.getHours()),H:i=>i.getHours(),h:i=>{let e=i.getHours();return e==0?12:e>12?e-12:e},AA:i=>i.getHours()>=12?"PM":"AM",aa:i=>i.getHours()>=12?"pm":"am",a:i=>i.getHours()>=12?"p":"a",mm:i=>vo(i.getMinutes()),m:i=>i.getMinutes(),ss:i=>vo(i.getSeconds()),s:i=>i.getSeconds(),fff:i=>my(i.getMilliseconds())};function Nu(i,e){e=e||py;let t=[],n=/\{([a-z]+)\}|[^{]+/gi,r;for(;r=n.exec(i);)t.push(r[0][0]=="{"?gy[r[1]]:r[0]);return s=>{let o="";for(let a=0;a<t.length;a++)o+=typeof t[a]=="string"?t[a]:t[a](s,e);return o}}const _y=new Intl.DateTimeFormat().resolvedOptions().timeZone;function vy(i,e){let t;return e=="UTC"||e=="Etc/UTC"?t=new Date(+i+i.getTimezoneOffset()*6e4):e==_y?t=i:(t=new Date(i.toLocaleString("en-US",{timeZone:e})),t.setMilliseconds(i.getMilliseconds())),t}const Yp=i=>i%1==0,tl=[1,2,2.5,5],xy=Oo(10,-32,0,tl),jp=Oo(10,0,32,tl),My=jp.filter(Yp),Nr=xy.concat(jp),Fu=`
`,$p="{YYYY}",Md=Fu+$p,Kp="{M}/{D}",wo=Fu+Kp,Ua=wo+"/{YY}",Zp="{aa}",Sy="{h}:{mm}",Ps=Sy+Zp,Sd=Fu+Ps,yd=":{ss}",Mt=null;function Jp(i){let e=i*1e3,t=e*60,n=t*60,r=n*24,s=r*30,o=r*365,l=(i==1?Oo(10,0,3,tl).filter(Yp):Oo(10,-3,0,tl)).concat([e,e*5,e*10,e*15,e*30,t,t*5,t*10,t*15,t*30,n,n*2,n*3,n*4,n*6,n*8,n*12,r,r*2,r*3,r*4,r*5,r*6,r*7,r*8,r*9,r*10,r*15,s,s*2,s*3,s*4,s*6,o,o*2,o*5,o*10,o*25,o*50,o*100]);const c=[[o,$p,Mt,Mt,Mt,Mt,Mt,Mt,1],[r*28,"{MMM}",Md,Mt,Mt,Mt,Mt,Mt,1],[r,Kp,Md,Mt,Mt,Mt,Mt,Mt,1],[n,"{h}"+Zp,Ua,Mt,wo,Mt,Mt,Mt,1],[t,Ps,Ua,Mt,wo,Mt,Mt,Mt,1],[e,yd,Ua+" "+Ps,Mt,wo+" "+Ps,Mt,Sd,Mt,1],[i,yd+".{fff}",Ua+" "+Ps,Mt,wo+" "+Ps,Mt,Sd,Mt,1]];function u(f){return(d,m,v,M,p,h)=>{let x=[],_=p>=o,y=p>=s&&p<o,D=f(v),b=Rt(D*i,3),R=Mc(D.getFullYear(),_?0:D.getMonth(),y||_?1:D.getDate()),q=Rt(R*i,3);if(y||_){let T=y?p/s:0,A=_?p/o:0,I=b==q?b:Rt(Mc(R.getFullYear()+A,R.getMonth()+T,1)*i,3),Y=new Date(jt(I/i)),J=Y.getFullYear(),N=Y.getMonth();for(let B=0;I<=M;B++){let V=Mc(J+A*B,N+T*B,1),W=V-f(Rt(V*i,3));I=Rt((+V+W)*i,3),I<=M&&x.push(I)}}else{let T=p>=r?r:p,A=Vn(v)-Vn(b),I=q+A+pl(b-q,T);x.push(I);let Y=f(I),J=Y.getHours()+Y.getMinutes()/t+Y.getSeconds()/n,N=p/n,B=d.axes[m]._space,V=h/B;for(;I=Rt(I+p,i==1?0:3),!(I>M);)if(N>1){let W=Vn(Rt(J+N,6))%24,Q=f(I).getHours()-W;Q>1&&(Q=-1),I-=Q*n,J=(J+N)%24;let ae=x[x.length-1];Rt((I-ae)/p,3)*V>=.7&&x.push(I)}else x.push(I)}return x}}return[l,c,u]}const[yy,Ey,Ty]=Jp(1),[by,Ay,wy]=Jp(.001);Oo(2,-53,53,[1]);function Ed(i,e){return i.map(t=>t.map((n,r)=>r==0||r==8||n==null?n:e(r==1||t[8]==0?n:t[1]+n)))}function Td(i,e){return(t,n,r,s,o)=>{let a=e.find(v=>o>=v[0])||e[e.length-1],l,c,u,f,d,m;return n.map(v=>{let M=i(v),p=M.getFullYear(),h=M.getMonth(),x=M.getDate(),_=M.getHours(),y=M.getMinutes(),D=M.getSeconds(),b=p!=l&&a[2]||h!=c&&a[3]||x!=u&&a[4]||_!=f&&a[5]||y!=d&&a[6]||D!=m&&a[7]||a[1];return l=p,c=h,u=x,f=_,d=y,m=D,b(M)})}}function Ry(i,e){let t=Nu(e);return(n,r,s,o,a)=>r.map(l=>t(i(l)))}function Mc(i,e,t){return new Date(i,e,t)}function bd(i,e){return e(i)}const Cy="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function Ad(i,e){return(t,n,r,s)=>s==null?Cu:e(i(n))}function Ly(i,e){let t=i.series[e];return t.width?t.stroke(i,e):t.points.width?t.points.stroke(i,e):null}function Py(i,e){return i.series[e].fill(i,e)}const Dy={show:!0,live:!0,isolate:!1,mount:ZS,markers:{show:!0,width:2,stroke:Ly,fill:Py,dash:"solid"},idx:null,idxs:null,values:[]};function Uy(i,e){let t=i.cursor.points,n=jn(),r=t.size(i,e);Ut(n,bo,r),Ut(n,Ao,r);let s=r/-2;Ut(n,"marginLeft",s),Ut(n,"marginTop",s);let o=t.width(i,e,r);return o&&Ut(n,"borderWidth",o),n}function Iy(i,e){let t=i.series[e].points;return t._fill||t._stroke}function Ny(i,e){let t=i.series[e].points;return t._stroke||t._fill}function Fy(i,e){return i.series[e].points.size}const Sc=[0,0];function Oy(i,e,t){return Sc[0]=e,Sc[1]=t,Sc}function Ia(i,e,t,n=!0){return r=>{r.button==0&&(!n||r.target==e)&&t(r)}}function yc(i,e,t,n=!0){return r=>{(!n||r.target==e)&&t(r)}}const By={show:!0,x:!0,y:!0,lock:!1,move:Oy,points:{one:!1,show:Uy,size:Fy,width:0,stroke:Ny,fill:Iy},bind:{mousedown:Ia,mouseup:Ia,click:Ia,dblclick:Ia,mousemove:yc,mouseleave:yc,mouseenter:yc},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(i,e)=>{e.stopPropagation(),e.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(i,e,t,n,r)=>n-r,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},Qp={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},Ou=qt({},Qp,{filter:zp}),em=qt({},Ou,{size:10}),tm=qt({},Qp,{show:!1}),Bu='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',nm="bold "+Bu,im=1.5,wd={show:!0,scale:"x",stroke:Ru,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:nm,side:2,grid:Ou,ticks:em,border:tm,font:Bu,lineGap:im,rotate:0},zy="Value",ky="Time",Rd={show:!0,scale:"x",auto:!1,sorted:1,min:wt,max:-wt,idxs:[]};function Hy(i,e,t,n,r){return e.map(s=>s==null?"":Uu(s))}function Gy(i,e,t,n,r,s,o){let a=[],l=vr.get(r)||0;t=o?t:Rt(pl(t,r),l);for(let c=t;c<=n;c=Rt(c+r,l))a.push(Object.is(c,-0)?0:c);return a}function fu(i,e,t,n,r,s,o){const a=[],l=i.scales[i.axes[e].scale].log,c=l==10?Hi:Fp,u=Vn(c(t));r=Ws(l,u),l==10&&(r=Nr[ci(r,Nr)]);let f=t,d=r*l;l==10&&(d=Nr[ci(d,Nr)]);do a.push(f),f=f+r,l==10&&!vr.has(f)&&(f=Rt(f,vr.get(r))),f>=d&&(r=f,d=r*l,l==10&&(d=Nr[ci(d,Nr)]));while(f<=n);return a}function Vy(i,e,t,n,r,s,o){let l=i.scales[i.axes[e].scale].asinh,c=n>l?fu(i,e,Tn(l,t),n,r):[l],u=n>=0&&t<=0?[0]:[];return(t<-l?fu(i,e,Tn(l,-n),-t,r):[l]).reverse().map(d=>-d).concat(u,c)}const rm=/./,Wy=/[12357]/,Xy=/[125]/,Cd=/1/,hu=(i,e,t,n)=>i.map((r,s)=>e==4&&r==0||s%n==0&&t.test(r.toExponential()[r<0?1:0])?r:null);function qy(i,e,t,n,r){let s=i.axes[t],o=s.scale,a=i.scales[o],l=i.valToPos,c=s._space,u=l(10,o),f=l(9,o)-u>=c?rm:l(7,o)-u>=c?Wy:l(5,o)-u>=c?Xy:Cd;if(f==Cd){let d=$t(l(1,o)-u);if(d<c)return hu(e.slice().reverse(),a.distr,f,$n(c/d)).reverse()}return hu(e,a.distr,f,1)}function Yy(i,e,t,n,r){let s=i.axes[t],o=s.scale,a=s._space,l=i.valToPos,c=$t(l(1,o)-l(2,o));return c<a?hu(e.slice().reverse(),3,rm,$n(a/c)).reverse():e}function jy(i,e,t,n){return n==null?Cu:e==null?"":Uu(e)}const Ld={show:!0,scale:"y",stroke:Ru,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:nm,side:3,grid:Ou,ticks:em,border:tm,font:Bu,lineGap:im,rotate:0};function $y(i,e){let t=3+(i||1)*2;return Rt(t*e,3)}function Ky(i,e){let{scale:t,idxs:n}=i.series[0],r=i._data[0],s=i.valToPos(r[n[0]],t,!0),o=i.valToPos(r[n[1]],t,!0),a=$t(o-s),l=i.series[e],c=a/(l.points.space*vt);return n[1]-n[0]<=c}const Pd={scale:null,auto:!0,sorted:0,min:wt,max:-wt},sm=(i,e,t,n,r)=>r,Dd={show:!0,auto:!0,sorted:0,gaps:sm,alpha:1,facets:[qt({},Pd,{scale:"x"}),qt({},Pd,{scale:"y"})]},Ud={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:sm,alpha:1,points:{show:Ky,filter:null},values:null,min:wt,max:-wt,idxs:[],path:null,clip:null};function Zy(i,e,t,n,r){return t/10}const om={time:yS,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},Jy=qt({},om,{time:!1,ori:1}),Id={};function am(i,e){let t=Id[i];return t||(t={key:i,plots:[],sub(n){t.plots.push(n)},unsub(n){t.plots=t.plots.filter(r=>r!=n)},pub(n,r,s,o,a,l,c){for(let u=0;u<t.plots.length;u++)t.plots[u]!=r&&t.plots[u].pub(n,r,s,o,a,l,c)}},i!=null&&(Id[i]=t)),t}const Ys=1,du=2;function Kr(i,e,t){const n=i.mode,r=i.series[e],s=n==2?i._data[e]:i._data,o=i.scales,a=i.bbox;let l=s[0],c=n==2?s[1]:s[e],u=n==2?o[r.facets[0].scale]:o[i.series[0].scale],f=n==2?o[r.facets[1].scale]:o[r.scale],d=a.left,m=a.top,v=a.width,M=a.height,p=i.valToPosH,h=i.valToPosV;return u.ori==0?t(r,l,c,u,f,p,h,d,m,v,M,_l,Qs,xl,cm,fm):t(r,l,c,u,f,h,p,m,d,M,v,vl,eo,Hu,um,hm)}function zu(i,e){let t=0,n=0,r=dt(i.bands,Iu);for(let s=0;s<r.length;s++){let o=r[s];o.series[0]==e?t=o.dir:o.series[1]==e&&(o.dir==1?n|=1:n|=2)}return[t,n==1?-1:n==2?1:n==3?2:0]}function Qy(i,e,t,n,r){let s=i.mode,o=i.series[e],a=s==2?o.facets[1].scale:o.scale,l=i.scales[a];return r==-1?l.min:r==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Gi(i,e,t,n,r,s){return Kr(i,e,(o,a,l,c,u,f,d,m,v,M,p)=>{let h=o.pxRound;const x=c.dir*(c.ori==0?1:-1),_=c.ori==0?Qs:eo;let y,D;x==1?(y=t,D=n):(y=n,D=t);let b=h(f(a[y],c,M,m)),R=h(d(l[y],u,p,v)),q=h(f(a[D],c,M,m)),T=h(d(s==1?u.max:u.min,u,p,v)),A=new Path2D(r);return _(A,q,T),_(A,b,T),_(A,b,R),A})}function gl(i,e,t,n,r,s){let o=null;if(i.length>0){o=new Path2D;const a=e==0?xl:Hu;let l=t;for(let f=0;f<i.length;f++){let d=i[f];if(d[1]>d[0]){let m=d[0]-l;m>0&&a(o,l,n,m,n+s),l=d[1]}}let c=t+r-l,u=10;c>0&&a(o,l,n-u/2,c,n+s+u)}return o}function eE(i,e,t){let n=i[i.length-1];n&&n[0]==e?n[1]=t:i.push([e,t])}function ku(i,e,t,n,r,s,o){let a=[],l=i.length;for(let c=r==1?t:n;c>=t&&c<=n;c+=r)if(e[c]===null){let f=c,d=c;if(r==1)for(;++c<=n&&e[c]===null;)d=c;else for(;--c>=t&&e[c]===null;)d=c;let m=s(i[f]),v=d==f?m:s(i[d]),M=f-r;m=o<=0&&M>=0&&M<l?s(i[M]):m;let h=d+r;v=o>=0&&h>=0&&h<l?s(i[h]):v,v>=m&&a.push([m,v])}return a}function Nd(i){return i==0?Bp:i==1?jt:e=>Ir(e,i)}function lm(i){let e=i==0?_l:vl,t=i==0?(r,s,o,a,l,c)=>{r.arcTo(s,o,a,l,c)}:(r,s,o,a,l,c)=>{r.arcTo(o,s,l,a,c)},n=i==0?(r,s,o,a,l)=>{r.rect(s,o,a,l)}:(r,s,o,a,l)=>{r.rect(o,s,l,a)};return(r,s,o,a,l,c=0,u=0)=>{c==0&&u==0?n(r,s,o,a,l):(c=hi(c,a/2,l/2),u=hi(u,a/2,l/2),e(r,s+c,o),t(r,s+a,o,s+a,o+l,c),t(r,s+a,o+l,s,o+l,u),t(r,s,o+l,s,o,u),t(r,s,o,s+a,o,c),r.closePath())}}const _l=(i,e,t)=>{i.moveTo(e,t)},vl=(i,e,t)=>{i.moveTo(t,e)},Qs=(i,e,t)=>{i.lineTo(e,t)},eo=(i,e,t)=>{i.lineTo(t,e)},xl=lm(0),Hu=lm(1),cm=(i,e,t,n,r,s)=>{i.arc(e,t,n,r,s)},um=(i,e,t,n,r,s)=>{i.arc(t,e,n,r,s)},fm=(i,e,t,n,r,s,o)=>{i.bezierCurveTo(e,t,n,r,s,o)},hm=(i,e,t,n,r,s,o)=>{i.bezierCurveTo(t,e,r,n,o,s)};function dm(i){return(e,t,n,r,s)=>Kr(e,t,(o,a,l,c,u,f,d,m,v,M,p)=>{let{pxRound:h,points:x}=o,_,y;c.ori==0?(_=_l,y=cm):(_=vl,y=um);const D=Rt(x.width*vt,3);let b=(x.size-x.width)/2*vt,R=Rt(b*2,3),q=new Path2D,T=new Path2D,{left:A,top:I,width:Y,height:J}=e.bbox;xl(T,A-R,I-R,Y+R*2,J+R*2);const N=B=>{if(l[B]!=null){let V=h(f(a[B],c,M,m)),W=h(d(l[B],u,p,v));_(q,V+b,W),y(q,V,W,b,0,Wa*2)}};if(s)s.forEach(N);else for(let B=n;B<=r;B++)N(B);return{stroke:D>0?q:null,fill:q,clip:T,flags:Ys|du}})}function pm(i){return(e,t,n,r,s,o)=>{n!=r&&(s!=n&&o!=n&&i(e,t,n),s!=r&&o!=r&&i(e,t,r),i(e,t,o))}}const tE=pm(Qs),nE=pm(eo);function mm(i){const e=dt(i==null?void 0:i.alignGaps,0);return(t,n,r,s)=>Kr(t,n,(o,a,l,c,u,f,d,m,v,M,p)=>{[r,s]=hl(l,r,s);let h=o.pxRound,x=J=>h(f(J,c,M,m)),_=J=>h(d(J,u,p,v)),y,D;c.ori==0?(y=Qs,D=tE):(y=eo,D=nE);const b=c.dir*(c.ori==0?1:-1),R={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Ys},q=R.stroke;let T=!1;if(s-r>=M*4){let J=z=>t.posToVal(z,c.key,!0),N=null,B=null,V,W,ie,te=x(a[b==1?r:s]),Q=x(a[r]),ae=x(a[s]),re=J(b==1?Q+1:ae-1);for(let z=b==1?r:s;z>=r&&z<=s;z+=b){let se=a[z],Se=(b==1?se<re:se>re)?te:x(se),ge=l[z];Se==te?ge!=null?(W=ge,N==null?(y(q,Se,_(W)),V=N=B=W):W<N?N=W:W>B&&(B=W)):ge===null&&(T=!0):(N!=null&&D(q,te,_(N),_(B),_(V),_(W)),ge!=null?(W=ge,y(q,Se,_(W)),N=B=V=W):(N=B=null,ge===null&&(T=!0)),te=Se,re=J(te+b))}N!=null&&N!=B&&ie!=te&&D(q,te,_(N),_(B),_(V),_(W))}else for(let J=b==1?r:s;J>=r&&J<=s;J+=b){let N=l[J];N===null?T=!0:N!=null&&y(q,x(a[J]),_(N))}let[I,Y]=zu(t,n);if(o.fill!=null||I!=0){let J=R.fill=new Path2D(q),N=o.fillTo(t,n,o.min,o.max,I),B=_(N),V=x(a[r]),W=x(a[s]);b==-1&&([W,V]=[V,W]),y(J,W,B),y(J,V,B)}if(!o.spanGaps){let J=[];T&&J.push(...ku(a,l,r,s,b,x,e)),R.gaps=J=o.gaps(t,n,r,s,J),R.clip=gl(J,c.ori,m,v,M,p)}return Y!=0&&(R.band=Y==2?[Gi(t,n,r,s,q,-1),Gi(t,n,r,s,q,1)]:Gi(t,n,r,s,q,Y)),R})}function iE(i){const e=dt(i.align,1),t=dt(i.ascDesc,!1),n=dt(i.alignGaps,0),r=dt(i.extend,!1);return(s,o,a,l)=>Kr(s,o,(c,u,f,d,m,v,M,p,h,x,_)=>{[a,l]=hl(f,a,l);let y=c.pxRound,{left:D,width:b}=s.bbox,R=Q=>y(v(Q,d,x,p)),q=Q=>y(M(Q,m,_,h)),T=d.ori==0?Qs:eo;const A={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:Ys},I=A.stroke,Y=d.dir*(d.ori==0?1:-1);let J=q(f[Y==1?a:l]),N=R(u[Y==1?a:l]),B=N,V=N;r&&e==-1&&(V=D,T(I,V,J)),T(I,N,J);for(let Q=Y==1?a:l;Q>=a&&Q<=l;Q+=Y){let ae=f[Q];if(ae==null)continue;let re=R(u[Q]),z=q(ae);e==1?T(I,re,J):T(I,B,z),T(I,re,z),J=z,B=re}let W=B;r&&e==1&&(W=D+b,T(I,W,J));let[ie,te]=zu(s,o);if(c.fill!=null||ie!=0){let Q=A.fill=new Path2D(I),ae=c.fillTo(s,o,c.min,c.max,ie),re=q(ae);T(Q,W,re),T(Q,V,re)}if(!c.spanGaps){let Q=[];Q.push(...ku(u,f,a,l,Y,R,n));let ae=c.width*vt/2,re=t||e==1?ae:-ae,z=t||e==-1?-ae:ae;Q.forEach(se=>{se[0]+=re,se[1]+=z}),A.gaps=Q=c.gaps(s,o,a,l,Q),A.clip=gl(Q,d.ori,p,h,x,_)}return te!=0&&(A.band=te==2?[Gi(s,o,a,l,I,-1),Gi(s,o,a,l,I,1)]:Gi(s,o,a,l,I,te)),A})}function Fd(i,e,t,n,r,s,o=wt){if(i.length>1){let a=null;for(let l=0,c=1/0;l<i.length;l++)if(e[l]!==void 0){if(a!=null){let u=$t(i[l]-i[a]);u<c&&(c=u,o=$t(t(i[l],n,r,s)-t(i[a],n,r,s)))}a=l}}return o}function rE(i){i=i||Do;const e=dt(i.size,[.6,wt,1]),t=i.align||0,n=i.gap||0;let r=i.radius;r=r==null?[0,0]:typeof r=="number"?[r,0]:r;const s=ut(r),o=1-e[0],a=dt(e[1],wt),l=dt(e[2],1),c=dt(i.disp,Do),u=dt(i.each,m=>{}),{fill:f,stroke:d}=c;return(m,v,M,p)=>Kr(m,v,(h,x,_,y,D,b,R,q,T,A,I)=>{let Y=h.pxRound,J=t,N=n*vt,B=a*vt,V=l*vt,W,ie;y.ori==0?[W,ie]=s(m,v):[ie,W]=s(m,v);const te=y.dir*(y.ori==0?1:-1);let Q=y.ori==0?xl:Hu,ae=y.ori==0?u:(ne,fe,Me,Fe,Ye,le,rt)=>{u(ne,fe,Me,Ye,Fe,rt,le)},re=dt(m.bands,Iu).find(ne=>ne.series[0]==v),z=re!=null?re.dir:0,se=h.fillTo(m,v,h.min,h.max,z),ve=Y(R(se,D,I,T)),Se,ge,ke,Be=A,be=Y(h.width*vt),Ke=!1,j=null,xt=null,Ue=null,Ve=null;f!=null&&(be==0||d!=null)&&(Ke=!0,j=f.values(m,v,M,p),xt=new Map,new Set(j).forEach(ne=>{ne!=null&&xt.set(ne,new Path2D)}),be>0&&(Ue=d.values(m,v,M,p),Ve=new Map,new Set(Ue).forEach(ne=>{ne!=null&&Ve.set(ne,new Path2D)})));let{x0:Le,size:mt}=c;if(Le!=null&&mt!=null){J=1,x=Le.values(m,v,M,p),Le.unit==2&&(x=x.map(Me=>m.posToVal(q+Me*A,y.key,!0)));let ne=mt.values(m,v,M,p);mt.unit==2?ge=ne[0]*A:ge=b(ne[0],y,A,q)-b(0,y,A,q),Be=Fd(x,_,b,y,A,q,Be),ke=Be-ge+N}else Be=Fd(x,_,b,y,A,q,Be),ke=Be*o+N,ge=Be-ke;ke<1&&(ke=0),be>=ge/2&&(be=0),ke<5&&(Y=Bp);let Ze=ke>0,L=Be-ke-(Ze?be:0);ge=Y(uu(L,V,B)),Se=(J==0?ge/2:J==te?0:ge)-J*te*((J==0?N/2:0)+(Ze?be/2:0));const E={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},$=Ke?null:new Path2D;let ue=null;if(re!=null)ue=m.data[re.series[1]];else{let{y0:ne,y1:fe}=c;ne!=null&&fe!=null&&(_=fe.values(m,v,M,p),ue=ne.values(m,v,M,p))}let ce=W*ge,ee=ie*ge;for(let ne=te==1?M:p;ne>=M&&ne<=p;ne+=te){let fe=_[ne];if(fe==null)continue;if(ue!=null){let Ce=ue[ne]??0;if(fe-Ce==0)continue;ve=R(Ce,D,I,T)}let Me=y.distr!=2||c!=null?x[ne]:ne,Fe=b(Me,y,A,q),Ye=R(dt(fe,se),D,I,T),le=Y(Fe-Se),rt=Y(Tn(Ye,ve)),Ge=Y(hi(Ye,ve)),Oe=rt-Ge;if(fe!=null){let Ce=fe<0?ee:ce,ye=fe<0?ce:ee;Ke?(be>0&&Ue[ne]!=null&&Q(Ve.get(Ue[ne]),le,Ge+Vn(be/2),ge,Tn(0,Oe-be),Ce,ye),j[ne]!=null&&Q(xt.get(j[ne]),le,Ge+Vn(be/2),ge,Tn(0,Oe-be),Ce,ye)):Q($,le,Ge+Vn(be/2),ge,Tn(0,Oe-be),Ce,ye),ae(m,v,ne,le-be/2,Ge,ge+be,Oe)}}return be>0?E.stroke=Ke?Ve:$:Ke||(E._fill=h.width==0?h._fill:h._stroke??h._fill,E.width=0),E.fill=Ke?xt:$,E})}function sE(i,e){const t=dt(e==null?void 0:e.alignGaps,0);return(n,r,s,o)=>Kr(n,r,(a,l,c,u,f,d,m,v,M,p,h)=>{[s,o]=hl(c,s,o);let x=a.pxRound,_=W=>x(d(W,u,p,v)),y=W=>x(m(W,f,h,M)),D,b,R;u.ori==0?(D=_l,R=Qs,b=fm):(D=vl,R=eo,b=hm);const q=u.dir*(u.ori==0?1:-1);let T=_(l[q==1?s:o]),A=T,I=[],Y=[];for(let W=q==1?s:o;W>=s&&W<=o;W+=q)if(c[W]!=null){let te=l[W],Q=_(te);I.push(A=Q),Y.push(y(c[W]))}const J={stroke:i(I,Y,D,R,b,x),fill:null,clip:null,band:null,gaps:null,flags:Ys},N=J.stroke;let[B,V]=zu(n,r);if(a.fill!=null||B!=0){let W=J.fill=new Path2D(N),ie=a.fillTo(n,r,a.min,a.max,B),te=y(ie);R(W,A,te),R(W,T,te)}if(!a.spanGaps){let W=[];W.push(...ku(l,c,s,o,q,_,t)),J.gaps=W=a.gaps(n,r,s,o,W),J.clip=gl(W,u.ori,v,M,p,h)}return V!=0&&(J.band=V==2?[Gi(n,r,s,o,N,-1),Gi(n,r,s,o,N,1)]:Gi(n,r,s,o,N,V)),J})}function oE(i){return sE(aE,i)}function aE(i,e,t,n,r,s){const o=i.length;if(o<2)return null;const a=new Path2D;if(t(a,i[0],e[0]),o==2)n(a,i[1],e[1]);else{let l=Array(o),c=Array(o-1),u=Array(o-1),f=Array(o-1);for(let d=0;d<o-1;d++)u[d]=e[d+1]-e[d],f[d]=i[d+1]-i[d],c[d]=u[d]/f[d];l[0]=c[0];for(let d=1;d<o-1;d++)c[d]===0||c[d-1]===0||c[d-1]>0!=c[d]>0?l[d]=0:(l[d]=3*(f[d-1]+f[d])/((2*f[d]+f[d-1])/c[d-1]+(f[d]+2*f[d-1])/c[d]),isFinite(l[d])||(l[d]=0));l[o-1]=c[o-2];for(let d=0;d<o-1;d++)r(a,i[d]+f[d]/3,e[d]+l[d]*f[d]/3,i[d+1]-f[d]/3,e[d+1]-l[d+1]*f[d]/3,i[d+1],e[d+1])}return a}const pu=new Set;function Od(){for(let i of pu)i.syncRect(!0)}Js&&(Vr(HS,Bs,Od),Vr(GS,Bs,Od,!0),Vr(Qa,Bs,()=>{Kt.pxRatio=vt}));const lE=mm(),cE=dm();function Bd(i,e,t,n){return(n?[i[0],i[1]].concat(i.slice(2)):[i[0]].concat(i.slice(1))).map((s,o)=>mu(s,o,e,t))}function uE(i,e){return i.map((t,n)=>n==0?{}:qt({},e,t))}function mu(i,e,t,n){return qt({},e==0?t:n,i)}function gm(i,e,t){return e==null?Xs:[e,t]}const fE=gm;function hE(i,e,t){return e==null?Xs:el(e,t,Du,!0)}function _m(i,e,t,n){return e==null?Xs:dl(e,t,i.scales[n].log,!1)}const dE=_m;function vm(i,e,t,n){return e==null?Xs:Pu(e,t,i.scales[n].log,!1)}const pE=vm;function mE(i,e,t,n,r){let s=Tn(gd(i),gd(e)),o=e-i,a=ci(r/n*o,t);do{let l=t[a],c=n*l/o;if(c>=r&&s+(l<5?vr.get(l):0)<=17)return[l,c]}while(++a<t.length);return[0,0]}function zd(i){let e,t;return i=i.replace(/(\d+)px/,(n,r)=>(e=jt((t=+r)*vt))+"px"),[i,e,t]}function gE(i){i.show&&[i.font,i.labelFont].forEach(e=>{let t=Rt(e[2]*vt,1);e[0]=e[0].replace(/[0-9.]+px/,t+"px"),e[1]=t})}function Kt(i,e,t){const n={mode:dt(i.mode,1)},r=n.mode;function s(g,S,C,P){let O=S.valToPct(g);return P+C*(S.dir==-1?1-O:O)}function o(g,S,C,P){let O=S.valToPct(g);return P+C*(S.dir==-1?O:1-O)}function a(g,S,C,P){return S.ori==0?s(g,S,C,P):o(g,S,C,P)}n.valToPosH=s,n.valToPosV=o;let l=!1;n.status=0;const c=n.root=jn(ES);if(i.id!=null&&(c.id=i.id),zn(c,i.class),i.title){let g=jn(AS,c);g.textContent=i.title}const u=li("canvas"),f=n.ctx=u.getContext("2d"),d=jn(wS,c);Vr("click",d,g=>{g.target===v&&(Lt!=is||Ft!=rs)&&un.click(n,g)},!0);const m=n.under=jn(RS,d);d.appendChild(u);const v=n.over=jn(CS,d);i=qs(i);const M=+dt(i.pxAlign,1),p=Nd(M);(i.plugins||[]).forEach(g=>{g.opts&&(i=g.opts(n,i)||i)});const h=i.ms||.001,x=n.series=r==1?Bd(i.series||[],Rd,Ud,!1):uE(i.series||[null],Dd),_=n.axes=Bd(i.axes||[],wd,Ld,!0),y=n.scales={},D=n.bands=i.bands||[];D.forEach(g=>{g.fill=ut(g.fill||null),g.dir=dt(g.dir,-1)});const b=r==2?x[1].facets[0].scale:x[0].scale,R={axes:Um,series:Rn},q=(i.drawOrder||["axes","series"]).map(g=>R[g]);function T(g){const S=g.distr==3?C=>Hi(C>0?C:g.clamp(n,C,g.min,g.max,g.key)):g.distr==4?C=>xc(C,g.asinh):g.distr==100?C=>g.fwd(C):C=>C;return C=>{let P=S(C),{_min:O,_max:X}=g,oe=X-O;return(P-O)/oe}}function A(g){let S=y[g];if(S==null){let C=(i.scales||Do)[g]||Do;if(C.from!=null){A(C.from);let P=qt({},y[C.from],C,{key:g});P.valToPct=T(P),y[g]=P}else{S=y[g]=qt({},g==b?om:Jy,C),S.key=g;let P=S.time,O=S.range,X=rr(O);if((g!=b||r==2&&!P)&&(X&&(O[0]==null||O[1]==null)&&(O={min:O[0]==null?dd:{mode:1,hard:O[0],soft:O[0]},max:O[1]==null?dd:{mode:1,hard:O[1],soft:O[1]}},X=!1),!X&&ml(O))){let oe=O;O=(de,_e,we)=>_e==null?Xs:el(_e,we,oe)}S.range=ut(O||(P?fE:g==b?S.distr==3?dE:S.distr==4?pE:gm:S.distr==3?_m:S.distr==4?vm:hE)),S.auto=ut(X?!1:S.auto),S.clamp=ut(S.clamp||Zy),S._min=S._max=null,S.valToPct=T(S)}}}A("x"),A("y"),r==1&&x.forEach(g=>{A(g.scale)}),_.forEach(g=>{A(g.scale)});for(let g in i.scales)A(g);const I=y[b],Y=I.distr;let J,N;I.ori==0?(zn(c,TS),J=s,N=o):(zn(c,bS),J=o,N=s);const B={};for(let g in y){let S=y[g];(S.min!=null||S.max!=null)&&(B[g]={min:S.min,max:S.max},S.min=S.max=null)}const V=i.tzDate||(g=>new Date(jt(g/h))),W=i.fmtDate||Nu,ie=h==1?Ty(V):wy(V),te=Td(V,Ed(h==1?Ey:Ay,W)),Q=Ad(V,bd(Cy,W)),ae=[],re=n.legend=qt({},Dy,i.legend),z=n.cursor=qt({},By,{drag:{y:r==2}},i.cursor),se=re.show,ve=z.show,Se=re.markers;re.idxs=ae,Se.width=ut(Se.width),Se.dash=ut(Se.dash),Se.stroke=ut(Se.stroke),Se.fill=ut(Se.fill);let ge,ke,Be,be=[],Ke=[],j,xt=!1,Ue={};if(re.live){const g=x[1]?x[1].values:null;xt=g!=null,j=xt?g(n,1,0):{_:0};for(let S in j)Ue[S]=Cu}if(se)if(ge=li("table",NS,c),Be=li("tbody",null,ge),re.mount(n,ge),xt){ke=li("thead",null,ge,Be);let g=li("tr",null,ke);li("th",null,g);for(var Ve in j)li("th",ed,g).textContent=Ve}else zn(ge,OS),re.live&&zn(ge,FS);const Le={show:!0},mt={show:!1};function Ze(g,S){if(S==0&&(xt||!re.live||r==2))return Xs;let C=[],P=li("tr",BS,Be,Be.childNodes[S]);zn(P,g.class),g.show||zn(P,Br);let O=li("th",null,P);if(Se.show){let de=jn(zS,O);if(S>0){let _e=Se.width(n,S);_e&&(de.style.border=_e+"px "+Se.dash(n,S)+" "+Se.stroke(n,S)),de.style.background=Se.fill(n,S)}}let X=jn(ed,O);g.label instanceof HTMLElement?X.appendChild(g.label):X.textContent=g.label,S>0&&(Se.show||(X.style.color=g.width>0?Se.stroke(n,S):Se.fill(n,S)),E("click",O,de=>{if(z._lock)return;St(de);let _e=x.indexOf(g);if((de.ctrlKey||de.metaKey)!=re.isolate){let we=x.some((Re,Pe)=>Pe>0&&Pe!=_e&&Re.show);x.forEach((Re,Pe)=>{Pe>0&&di(Pe,we?Pe==_e?Le:mt:Le,!0,Wt.setSeries)})}else di(_e,{show:!g.show},!0,Wt.setSeries)},!1),ln&&E(rd,O,de=>{z._lock||(St(de),di(x.indexOf(g),os,!0,Wt.setSeries))},!1));for(var oe in j){let de=li("td",kS,P);de.textContent="--",C.push(de)}return[P,C]}const L=new Map;function E(g,S,C,P=!0){const O=L.get(S)||{},X=z.bind[g](n,S,C,P);X&&(Vr(g,S,O[g]=X),L.set(S,O))}function $(g,S,C){const P=L.get(S)||{};for(let O in P)(g==null||O==g)&&(cu(O,S,P[O]),delete P[O]);g==null&&L.delete(S)}let ue=0,ce=0,ee=0,ne=0,fe=0,Me=0,Fe=fe,Ye=Me,le=ee,rt=ne,Ge=0,Oe=0,Ce=0,ye=0;n.bbox={};let U=!1,pe=!1,De=!1,Ae=!1,he=!1,F=!1;function me(g,S,C){(C||g!=n.width||S!=n.height)&&Te(g,S),Qr(!1),De=!0,pe=!0,es()}function Te(g,S){n.width=ue=ee=g,n.height=ce=ne=S,fe=Me=0,ot(),Nt();let C=n.bbox;Ge=C.left=Ir(fe*vt,.5),Oe=C.top=Ir(Me*vt,.5),Ce=C.width=Ir(ee*vt,.5),ye=C.height=Ir(ne*vt,.5)}const Xe=3;function He(){let g=!1,S=0;for(;!g;){S++;let C=Pm(S),P=Dm(S);g=S==Xe||C&&P,g||(Te(n.width,n.height),pe=!0)}}function st({width:g,height:S}){me(g,S)}n.setSize=st;function ot(){let g=!1,S=!1,C=!1,P=!1;_.forEach((O,X)=>{if(O.show&&O._show){let{side:oe,_size:de}=O,_e=oe%2,we=O.label!=null?O.labelSize:0,Re=de+we;Re>0&&(_e?(ee-=Re,oe==3?(fe+=Re,P=!0):C=!0):(ne-=Re,oe==0?(Me+=Re,g=!0):S=!0))}}),Ei[0]=g,Ei[1]=C,Ei[2]=S,Ei[3]=P,ee-=Z[1]+Z[3],fe+=Z[3],ne-=Z[2]+Z[0],Me+=Z[0]}function Nt(){let g=fe+ee,S=Me+ne,C=fe,P=Me;function O(X,oe){switch(X){case 1:return g+=oe,g-oe;case 2:return S+=oe,S-oe;case 3:return C-=oe,C+oe;case 0:return P-=oe,P+oe}}_.forEach((X,oe)=>{if(X.show&&X._show){let de=X.side;X._pos=O(de,X._size),X.label!=null&&(X._lpos=O(de,X.labelSize))}})}if(z.dataIdx==null){let g=z.hover,S=g.skip=new Set(g.skip??[]);S.add(void 0);let C=g.prox=ut(g.prox),P=g.bias??(g.bias=0);z.dataIdx=(O,X,oe,de)=>{if(X==0)return oe;let _e=oe,we=C(O,X,oe,de)??wt,Re=we>=0&&we<wt,Pe=I.ori==0?ee:ne,et=z.left,_t=e[0],ht=e[X];if(S.has(ht[oe])){_e=null;let lt=null,$e=null,ze;if(P==0||P==-1)for(ze=oe;lt==null&&ze-- >0;)S.has(ht[ze])||(lt=ze);if(P==0||P==1)for(ze=oe;$e==null&&ze++<ht.length;)S.has(ht[ze])||($e=ze);if(lt!=null||$e!=null)if(Re){let Dt=lt==null?-1/0:J(_t[lt],I,Pe,0),Ht=$e==null?1/0:J(_t[$e],I,Pe,0),sn=et-Dt,Et=Ht-et;sn<=Et?sn<=we&&(_e=lt):Et<=we&&(_e=$e)}else _e=$e==null?lt:lt==null?$e:oe-lt<=$e-oe?lt:$e}else Re&&$t(et-J(_t[oe],I,Pe,0))>we&&(_e=null);return _e}}const St=g=>{z.event=g};z.idxs=ae,z._lock=!1;let je=z.points;je.show=ut(je.show),je.size=ut(je.size),je.stroke=ut(je.stroke),je.width=ut(je.width),je.fill=ut(je.fill);const gt=n.focus=qt({},i.focus||{alpha:.3},z.focus),ln=gt.prox>=0,Si=ln&&je.one;let wn=[],ti=[],yi=[];function Sr(g,S){let C=je.show(n,S);if(C instanceof HTMLElement)return zn(C,IS),zn(C,g.class),_i(C,-10,-10,ee,ne),v.insertBefore(C,wn[S]),C}function to(g,S){if(r==1||S>0){let C=r==1&&y[g.scale].time,P=g.value;g.value=C?xd(P)?Ad(V,bd(P,W)):P||Q:P||jy,g.label=g.label||(C?ky:zy)}if(Si||S>0){g.width=g.width==null?1:g.width,g.paths=g.paths||lE||JS,g.fillTo=ut(g.fillTo||Qy),g.pxAlign=+dt(g.pxAlign,M),g.pxRound=Nd(g.pxAlign),g.stroke=ut(g.stroke||null),g.fill=ut(g.fill||null),g._stroke=g._fill=g._paths=g._focus=null;let C=$y(Tn(1,g.width),1),P=g.points=qt({},{size:C,width:Tn(1,C*.2),stroke:g.stroke,space:C*2,paths:cE,_stroke:null,_fill:null},g.points);P.show=ut(P.show),P.filter=ut(P.filter),P.fill=ut(P.fill),P.stroke=ut(P.stroke),P.paths=ut(P.paths),P.pxAlign=g.pxAlign}if(se){let C=Ze(g,S);be.splice(S,0,C[0]),Ke.splice(S,0,C[1]),re.values.push(null)}if(ve){ae.splice(S,0,null);let C=null;Si?S==0&&(C=Sr(g,S)):S>0&&(C=Sr(g,S)),wn.splice(S,0,C),ti.splice(S,0,0),yi.splice(S,0,0)}rn("addSeries",S)}function $o(g,S){S=S??x.length,g=r==1?mu(g,S,Rd,Ud):mu(g,S,{},Dd),x.splice(S,0,g),to(x[S],S)}n.addSeries=$o;function yl(g){if(x.splice(g,1),se){re.values.splice(g,1),Ke.splice(g,1);let S=be.splice(g,1)[0];$(null,S.firstChild),S.remove()}ve&&(ae.splice(g,1),wn.splice(g,1)[0].remove(),ti.splice(g,1),yi.splice(g,1)),rn("delSeries",g)}n.delSeries=yl;const Ei=[!1,!1,!1,!1];function El(g,S){if(g._show=g.show,g.show){let C=g.side%2,P=y[g.scale];P==null&&(g.scale=C?x[1].scale:b,P=y[g.scale]);let O=P.time;g.size=ut(g.size),g.space=ut(g.space),g.rotate=ut(g.rotate),rr(g.incrs)&&g.incrs.forEach(oe=>{!vr.has(oe)&&vr.set(oe,Hp(oe))}),g.incrs=ut(g.incrs||(P.distr==2?My:O?h==1?yy:by:Nr)),g.splits=ut(g.splits||(O&&P.distr==1?ie:P.distr==3?fu:P.distr==4?Vy:Gy)),g.stroke=ut(g.stroke),g.grid.stroke=ut(g.grid.stroke),g.ticks.stroke=ut(g.ticks.stroke),g.border.stroke=ut(g.border.stroke);let X=g.values;g.values=rr(X)&&!rr(X[0])?ut(X):O?rr(X)?Td(V,Ed(X,W)):xd(X)?Ry(V,X):X||te:X||Hy,g.filter=ut(g.filter||(P.distr>=3&&P.log==10?qy:P.distr==3&&P.log==2?Yy:zp)),g.font=zd(g.font),g.labelFont=zd(g.labelFont),g._size=g.size(n,null,S,0),g._space=g._rotate=g._incrs=g._found=g._splits=g._values=null,g._size>0&&(Ei[S]=!0,g._el=jn(LS,d))}}function w(g,S,C,P){let[O,X,oe,de]=C,_e=S%2,we=0;return _e==0&&(de||X)&&(we=S==0&&!O||S==2&&!oe?jt(wd.size/3):0),_e==1&&(O||oe)&&(we=S==1&&!X||S==3&&!de?jt(Ld.size/2):0),we}const H=n.padding=(i.padding||[w,w,w,w]).map(g=>ut(dt(g,w))),Z=n._padding=H.map((g,S)=>g(n,S,Ei,0));let K,G=null,xe=null;const Ie=r==1?x[0].idxs:null;let Ne=null,We=!1;function tt(g,S){if(e=g??[],n.data=n._data=e,r==2){K=0;for(let C=1;C<x.length;C++)K+=e[C][0].length}else{e.length==0&&(n.data=n._data=e=[[]]),Ne=e[0],K=Ne.length;let C=e;if(Y==2){C=e.slice();let P=C[0]=Array(K);for(let O=0;O<K;O++)P[O]=O}n._data=e=C}if(Qr(!0),rn("setData"),Y==2&&(De=!0),S!==!1){let C=I;C.auto(n,We)?Je():ji(b,C.min,C.max),Ae=Ae||z.left>=0,F=!0,es()}}n.setData=tt;function Je(){We=!0;let g,S;r==1&&(K>0?(G=Ie[0]=0,xe=Ie[1]=K-1,g=e[0][G],S=e[0][xe],Y==2?(g=G,S=xe):g==S&&(Y==3?[g,S]=dl(g,g,I.log,!1):Y==4?[g,S]=Pu(g,g,I.log,!1):I.time?S=g+jt(86400/h):[g,S]=el(g,S,Du,!0))):(G=Ie[0]=g=null,xe=Ie[1]=S=null)),ji(b,g,S)}let Qe,yt,cn,zt,Dn,bt,nt,yr,Ct,kt;function no(g,S,C,P,O,X){g??(g=nd),C??(C=Iu),P??(P="butt"),O??(O=nd),X??(X="round"),g!=Qe&&(f.strokeStyle=Qe=g),O!=yt&&(f.fillStyle=yt=O),S!=cn&&(f.lineWidth=cn=S),X!=Dn&&(f.lineJoin=Dn=X),P!=bt&&(f.lineCap=bt=P),C!=zt&&f.setLineDash(zt=C)}function qi(g,S,C,P){S!=yt&&(f.fillStyle=yt=S),g!=nt&&(f.font=nt=g),C!=yr&&(f.textAlign=yr=C),P!=Ct&&(f.textBaseline=Ct=P)}function Er(g,S,C,P,O=0){if(P.length>0&&g.auto(n,We)&&(S==null||S.min==null)){let X=dt(G,0),oe=dt(xe,P.length-1),de=C.min==null?qS(P,X,oe,O,g.distr==3):[C.min,C.max];g.min=hi(g.min,C.min=de[0]),g.max=Tn(g.max,C.max=de[1])}}const Yt={min:null,max:null};function Ti(){for(let P in y){let O=y[P];B[P]==null&&(O.min==null||B[b]!=null&&O.auto(n,We))&&(B[P]=Yt)}for(let P in y){let O=y[P];B[P]==null&&O.from!=null&&B[O.from]!=null&&(B[P]=Yt)}B[b]!=null&&Qr(!0);let g={};for(let P in B){let O=B[P];if(O!=null){let X=g[P]=qs(y[P],ty);if(O.min!=null)qt(X,O);else if(P!=b||r==2)if(K==0&&X.from==null){let oe=X.range(n,null,null,P);X.min=oe[0],X.max=oe[1]}else X.min=wt,X.max=-wt}}if(K>0){x.forEach((P,O)=>{if(r==1){let X=P.scale,oe=B[X];if(oe==null)return;let de=g[X];if(O==0){let _e=de.range(n,de.min,de.max,X);de.min=_e[0],de.max=_e[1],G=ci(de.min,e[0]),xe=ci(de.max,e[0]),xe-G>1&&(e[0][G]<de.min&&G++,e[0][xe]>de.max&&xe--),P.min=Ne[G],P.max=Ne[xe]}else P.show&&P.auto&&Er(de,oe,P,e[O],P.sorted);P.idxs[0]=G,P.idxs[1]=xe}else if(O>0&&P.show&&P.auto){let[X,oe]=P.facets,de=X.scale,_e=oe.scale,[we,Re]=e[O],Pe=g[de],et=g[_e];Pe!=null&&Er(Pe,B[de],X,we,X.sorted),et!=null&&Er(et,B[_e],oe,Re,oe.sorted),P.min=oe.min,P.max=oe.max}});for(let P in g){let O=g[P],X=B[P];if(O.from==null&&(X==null||X.min==null)){let oe=O.range(n,O.min==wt?null:O.min,O.max==-wt?null:O.max,P);O.min=oe[0],O.max=oe[1]}}}for(let P in g){let O=g[P];if(O.from!=null){let X=g[O.from];if(X.min==null)O.min=O.max=null;else{let oe=O.range(n,X.min,X.max,P);O.min=oe[0],O.max=oe[1]}}}let S={},C=!1;for(let P in g){let O=g[P],X=y[P];if(X.min!=O.min||X.max!=O.max){X.min=O.min,X.max=O.max;let oe=X.distr;X._min=oe==3?Hi(X.min):oe==4?xc(X.min,X.asinh):oe==100?X.fwd(X.min):X.min,X._max=oe==3?Hi(X.max):oe==4?xc(X.max,X.asinh):oe==100?X.fwd(X.max):X.max,S[P]=C=!0}}if(C){x.forEach((P,O)=>{r==2?O>0&&S.y&&(P._paths=null):S[P.scale]&&(P._paths=null)});for(let P in S)De=!0,rn("setScale",P);ve&&z.left>=0&&(Ae=F=!0)}for(let P in B)B[P]=null}function io(g){let S=uu(G-1,0,K-1),C=uu(xe+1,0,K-1);for(;g[S]==null&&S>0;)S--;for(;g[C]==null&&C<K-1;)C++;return[S,C]}function Rn(){if(K>0){let g=x.some(S=>S._focus)&&kt!=gt.alpha;g&&(f.globalAlpha=kt=gt.alpha),x.forEach((S,C)=>{if(C>0&&S.show&&(Jr(C,!1),Jr(C,!0),S._paths==null)){let P=kt;kt!=S.alpha&&(f.globalAlpha=kt=S.alpha);let O=r==2?[0,e[C][0].length-1]:io(e[C]);S._paths=S.paths(n,C,O[0],O[1]),kt!=P&&(f.globalAlpha=kt=P)}}),x.forEach((S,C)=>{if(C>0&&S.show){let P=kt;kt!=S.alpha&&(f.globalAlpha=kt=S.alpha),S._paths!=null&&Ko(C,!1);{let O=S._paths!=null?S._paths.gaps:null,X=S.points.show(n,C,G,xe,O),oe=S.points.filter(n,C,X,O);(X||oe)&&(S.points._paths=S.points.paths(n,C,G,xe,oe),Ko(C,!0))}kt!=P&&(f.globalAlpha=kt=P),rn("drawSeries",C)}}),g&&(f.globalAlpha=kt=1)}}function Jr(g,S){let C=S?x[g].points:x[g];C._stroke=C.stroke(n,g),C._fill=C.fill(n,g)}function Ko(g,S){let C=S?x[g].points:x[g],{stroke:P,fill:O,clip:X,flags:oe,_stroke:de=C._stroke,_fill:_e=C._fill,_width:we=C.width}=C._paths;we=Rt(we*vt,3);let Re=null,Pe=we%2/2;S&&_e==null&&(_e=we>0?"#fff":de);let et=C.pxAlign==1&&Pe>0;if(et&&f.translate(Pe,Pe),!S){let _t=Ge-we/2,ht=Oe-we/2,lt=Ce+we,$e=ye+we;Re=new Path2D,Re.rect(_t,ht,lt,$e)}S?Tl(de,we,C.dash,C.cap,_e,P,O,oe,X):Zo(g,de,we,C.dash,C.cap,_e,P,O,oe,Re,X),et&&f.translate(-Pe,-Pe)}function Zo(g,S,C,P,O,X,oe,de,_e,we,Re){let Pe=!1;_e!=0&&D.forEach((et,_t)=>{if(et.series[0]==g){let ht=x[et.series[1]],lt=e[et.series[1]],$e=(ht._paths||Do).band;rr($e)&&($e=et.dir==1?$e[0]:$e[1]);let ze,Dt=null;ht.show&&$e&&jS(lt,G,xe)?(Dt=et.fill(n,_t)||X,ze=ht._paths.clip):$e=null,Tl(S,C,P,O,Dt,oe,de,_e,we,Re,ze,$e),Pe=!0}}),Pe||Tl(S,C,P,O,X,oe,de,_e,we,Re)}const Zu=Ys|du;function Tl(g,S,C,P,O,X,oe,de,_e,we,Re,Pe){no(g,S,C,P,O),(_e||we||Pe)&&(f.save(),_e&&f.clip(_e),we&&f.clip(we)),Pe?(de&Zu)==Zu?(f.clip(Pe),Re&&f.clip(Re),Qo(O,oe),Jo(g,X,S)):de&du?(Qo(O,oe),f.clip(Pe),Jo(g,X,S)):de&Ys&&(f.save(),f.clip(Pe),Re&&f.clip(Re),Qo(O,oe),f.restore(),Jo(g,X,S)):(Qo(O,oe),Jo(g,X,S)),(_e||we||Pe)&&f.restore()}function Jo(g,S,C){C>0&&(S instanceof Map?S.forEach((P,O)=>{f.strokeStyle=Qe=O,f.stroke(P)}):S!=null&&g&&f.stroke(S))}function Qo(g,S){S instanceof Map?S.forEach((C,P)=>{f.fillStyle=yt=P,f.fill(C)}):S!=null&&g&&f.fill(S)}function Lm(g,S,C,P){let O=_[g],X;if(P<=0)X=[0,0];else{let oe=O._space=O.space(n,g,S,C,P),de=O._incrs=O.incrs(n,g,S,C,P,oe);X=mE(S,C,de,P,oe)}return O._found=X}function bl(g,S,C,P,O,X,oe,de,_e,we){let Re=oe%2/2;M==1&&f.translate(Re,Re),no(de,oe,_e,we,de),f.beginPath();let Pe,et,_t,ht,lt=O+(P==0||P==3?-X:X);C==0?(et=O,ht=lt):(Pe=O,_t=lt);for(let $e=0;$e<g.length;$e++)S[$e]!=null&&(C==0?Pe=_t=g[$e]:et=ht=g[$e],f.moveTo(Pe,et),f.lineTo(_t,ht));f.stroke(),M==1&&f.translate(-Re,-Re)}function Pm(g){let S=!0;return _.forEach((C,P)=>{if(!C.show)return;let O=y[C.scale];if(O.min==null){C._show&&(S=!1,C._show=!1,Qr(!1));return}else C._show||(S=!1,C._show=!0,Qr(!1));let X=C.side,oe=X%2,{min:de,max:_e}=O,[we,Re]=Lm(P,de,_e,oe==0?ee:ne);if(Re==0)return;let Pe=O.distr==2,et=C._splits=C.splits(n,P,de,_e,we,Re,Pe),_t=O.distr==2?et.map(ze=>Ne[ze]):et,ht=O.distr==2?Ne[et[1]]-Ne[et[0]]:we,lt=C._values=C.values(n,C.filter(n,_t,P,Re,ht),P,Re,ht);C._rotate=X==2?C.rotate(n,lt,P,Re):0;let $e=C._size;C._size=$n(C.size(n,lt,P,g)),$e!=null&&C._size!=$e&&(S=!1)}),S}function Dm(g){let S=!0;return H.forEach((C,P)=>{let O=C(n,P,Ei,g);O!=Z[P]&&(S=!1),Z[P]=O}),S}function Um(){for(let g=0;g<_.length;g++){let S=_[g];if(!S.show||!S._show)continue;let C=S.side,P=C%2,O,X,oe=S.stroke(n,g),de=C==0||C==3?-1:1,[_e,we]=S._found;if(S.label!=null){let _n=S.labelGap*de,Nn=jt((S._lpos+_n)*vt);qi(S.labelFont[0],oe,"center",C==2?_o:td),f.save(),P==1?(O=X=0,f.translate(Nn,jt(Oe+ye/2)),f.rotate((C==3?-Wa:Wa)/2)):(O=jt(Ge+Ce/2),X=Nn);let Ar=Op(S.label)?S.label(n,g,_e,we):S.label;f.fillText(Ar,O,X),f.restore()}if(we==0)continue;let Re=y[S.scale],Pe=P==0?Ce:ye,et=P==0?Ge:Oe,_t=S._splits,ht=Re.distr==2?_t.map(_n=>Ne[_n]):_t,lt=Re.distr==2?Ne[_t[1]]-Ne[_t[0]]:_e,$e=S.ticks,ze=S.border,Dt=$e.show?$e.size:0,Ht=jt(Dt*vt),sn=jt((S.alignTo==2?S._size-Dt-S.gap:S.gap)*vt),Et=S._rotate*-Wa/180,Gt=p(S._pos*vt),Un=(Ht+sn)*de,gn=Gt+Un;X=P==0?gn:0,O=P==1?gn:0;let Xn=S.font[0],ni=S.align==1?Ls:S.align==2?gc:Et>0?Ls:Et<0?gc:P==0?"center":C==3?gc:Ls,mi=Et||P==1?"middle":C==2?_o:td;qi(Xn,oe,ni,mi);let In=S.font[1]*S.lineGap,qn=_t.map(_n=>p(a(_n,Re,Pe,et))),ii=S._values;for(let _n=0;_n<ii.length;_n++){let Nn=ii[_n];if(Nn!=null){P==0?O=qn[_n]:X=qn[_n],Nn=""+Nn;let Ar=Nn.indexOf(`
`)==-1?[Nn]:Nn.split(/\n/gm);for(let vn=0;vn<Ar.length;vn++){let _f=Ar[vn];Et?(f.save(),f.translate(O,X+vn*In),f.rotate(Et),f.fillText(_f,0,0),f.restore()):f.fillText(_f,O,X+vn*In)}}}$e.show&&bl(qn,$e.filter(n,ht,g,we,lt),P,C,Gt,Ht,Rt($e.width*vt,3),$e.stroke(n,g),$e.dash,$e.cap);let gi=S.grid;gi.show&&bl(qn,gi.filter(n,ht,g,we,lt),P,P==0?2:1,P==0?Oe:Ge,P==0?ye:Ce,Rt(gi.width*vt,3),gi.stroke(n,g),gi.dash,gi.cap),ze.show&&bl([Gt],[1],P==0?1:0,P==0?1:2,P==1?Oe:Ge,P==1?ye:Ce,Rt(ze.width*vt,3),ze.stroke(n,g),ze.dash,ze.cap)}rn("drawAxes")}function Qr(g){x.forEach((S,C)=>{C>0&&(S._paths=null,g&&(r==1?(S.min=null,S.max=null):S.facets.forEach(P=>{P.min=null,P.max=null})))})}let ea=!1,Al=!1,ro=[];function Im(){Al=!1;for(let g=0;g<ro.length;g++)rn(...ro[g]);ro.length=0}function es(){ea||(ly(Ju),ea=!0)}function Nm(g,S=!1){ea=!0,Al=S,g(n),Ju(),S&&ro.length>0&&queueMicrotask(Im)}n.batch=Nm;function Ju(){if(U&&(Ti(),U=!1),De&&(He(),De=!1),pe){if(Ut(m,Ls,fe),Ut(m,_o,Me),Ut(m,bo,ee),Ut(m,Ao,ne),Ut(v,Ls,fe),Ut(v,_o,Me),Ut(v,bo,ee),Ut(v,Ao,ne),Ut(d,bo,ue),Ut(d,Ao,ce),u.width=jt(ue*vt),u.height=jt(ce*vt),_.forEach(({_el:g,_show:S,_size:C,_pos:P,side:O})=>{if(g!=null)if(S){let X=O===3||O===0?C:0,oe=O%2==1;Ut(g,oe?"left":"top",P-X),Ut(g,oe?"width":"height",C),Ut(g,oe?"top":"left",oe?Me:fe),Ut(g,oe?"height":"width",oe?ne:ee),lu(g,Br)}else zn(g,Br)}),Qe=yt=cn=Dn=bt=nt=yr=Ct=zt=null,kt=1,ao(!0),fe!=Fe||Me!=Ye||ee!=le||ne!=rt){Qr(!1);let g=ee/le,S=ne/rt;if(ve&&!Ae&&z.left>=0){z.left*=g,z.top*=S,ts&&_i(ts,jt(z.left),0,ee,ne),ns&&_i(ns,0,jt(z.top),ee,ne);for(let C=0;C<wn.length;C++){let P=wn[C];P!=null&&(ti[C]*=g,yi[C]*=S,_i(P,$n(ti[C]),$n(yi[C]),ee,ne))}}if(Pt.show&&!he&&Pt.left>=0&&Pt.width>0){Pt.left*=g,Pt.width*=g,Pt.top*=S,Pt.height*=S;for(let C in Dl)Ut(ss,C,Pt[C])}Fe=fe,Ye=Me,le=ee,rt=ne}rn("setSize"),pe=!1}ue>0&&ce>0&&(f.clearRect(0,0,u.width,u.height),rn("drawClear"),q.forEach(g=>g()),rn("draw")),Pt.show&&he&&(ta(Pt),he=!1),ve&&Ae&&(br(null,!0,!1),Ae=!1),re.show&&re.live&&F&&(Ll(),F=!1),l||(l=!0,n.status=1,rn("ready")),We=!1,ea=!1}n.redraw=(g,S)=>{De=S||!1,g!==!1?ji(b,I.min,I.max):es()};function wl(g,S){let C=y[g];if(C.from==null){if(K==0){let P=C.range(n,S.min,S.max,g);S.min=P[0],S.max=P[1]}if(S.min>S.max){let P=S.min;S.min=S.max,S.max=P}if(K>1&&S.min!=null&&S.max!=null&&S.max-S.min<1e-16)return;g==b&&C.distr==2&&K>0&&(S.min=ci(S.min,e[0]),S.max=ci(S.max,e[0]),S.min==S.max&&S.max++),B[g]=S,U=!0,es()}}n.setScale=wl;let Rl,Cl,ts,ns,Qu,ef,is,rs,tf,nf,Lt,Ft,Yi=!1;const un=z.drag;let tn=un.x,nn=un.y;ve&&(z.x&&(Rl=jn(DS,v)),z.y&&(Cl=jn(US,v)),I.ori==0?(ts=Rl,ns=Cl):(ts=Cl,ns=Rl),Lt=z.left,Ft=z.top);const Pt=n.select=qt({show:!0,over:!0,left:0,width:0,top:0,height:0},i.select),ss=Pt.show?jn(PS,Pt.over?v:m):null;function ta(g,S){if(Pt.show){for(let C in g)Pt[C]=g[C],C in Dl&&Ut(ss,C,g[C]);S!==!1&&rn("setSelect")}}n.setSelect=ta;function Fm(g){if(x[g].show)se&&lu(be[g],Br);else if(se&&zn(be[g],Br),ve){let C=Si?wn[0]:wn[g];C!=null&&_i(C,-10,-10,ee,ne)}}function ji(g,S,C){wl(g,{min:S,max:C})}function di(g,S,C,P){S.focus!=null&&Hm(g),S.show!=null&&x.forEach((O,X)=>{X>0&&(g==X||g==null)&&(O.show=S.show,Fm(X),r==2?(ji(O.facets[0].scale,null,null),ji(O.facets[1].scale,null,null)):ji(O.scale,null,null),es())}),C!==!1&&rn("setSeries",g,S),P&&lo("setSeries",n,g,S)}n.setSeries=di;function Om(g,S){qt(D[g],S)}function Bm(g,S){g.fill=ut(g.fill||null),g.dir=dt(g.dir,-1),S=S??D.length,D.splice(S,0,g)}function zm(g){g==null?D.length=0:D.splice(g,1)}n.addBand=Bm,n.setBand=Om,n.delBand=zm;function km(g,S){x[g].alpha=S,ve&&wn[g]!=null&&(wn[g].style.opacity=S),se&&be[g]&&(be[g].style.opacity=S)}let bi,$i,Tr;const os={focus:!0};function Hm(g){if(g!=Tr){let S=g==null,C=gt.alpha!=1;x.forEach((P,O)=>{if(r==1||O>0){let X=S||O==0||O==g;P._focus=S?null:X,C&&km(O,X?1:gt.alpha)}}),Tr=g,C&&es()}}se&&ln&&E(sd,ge,g=>{z._lock||(St(g),Tr!=null&&di(null,os,!0,Wt.setSeries))});function pi(g,S,C){let P=y[S];C&&(g=g/vt-(P.ori==1?Me:fe));let O=ee;P.ori==1&&(O=ne,g=O-g),P.dir==-1&&(g=O-g);let X=P._min,oe=P._max,de=g/O,_e=X+(oe-X)*de,we=P.distr;return we==3?Ws(10,_e):we==4?KS(_e,P.asinh):we==100?P.bwd(_e):_e}function Gm(g,S){let C=pi(g,b,S);return ci(C,e[0],G,xe)}n.valToIdx=g=>ci(g,e[0]),n.posToIdx=Gm,n.posToVal=pi,n.valToPos=(g,S,C)=>y[S].ori==0?s(g,y[S],C?Ce:ee,C?Ge:0):o(g,y[S],C?ye:ne,C?Oe:0),n.setCursor=(g,S,C)=>{Lt=g.left,Ft=g.top,br(null,S,C)};function rf(g,S){Ut(ss,Ls,Pt.left=g),Ut(ss,bo,Pt.width=S)}function sf(g,S){Ut(ss,_o,Pt.top=g),Ut(ss,Ao,Pt.height=S)}let so=I.ori==0?rf:sf,oo=I.ori==1?rf:sf;function Vm(){if(se&&re.live)for(let g=r==2?1:0;g<x.length;g++){if(g==0&&xt)continue;let S=re.values[g],C=0;for(let P in S)Ke[g][C++].firstChild.nodeValue=S[P]}}function Ll(g,S){if(g!=null&&(g.idxs?g.idxs.forEach((C,P)=>{ae[P]=C}):ey(g.idx)||ae.fill(g.idx),re.idx=ae[0]),se&&re.live){for(let C=0;C<x.length;C++)(C>0||r==1&&!xt)&&Wm(C,ae[C]);Vm()}F=!1,S!==!1&&rn("setLegend")}n.setLegend=Ll;function Wm(g,S){let C=x[g],P=g==0&&Y==2?Ne:e[g],O;xt?O=C.values(n,g,S)??Ue:(O=C.value(n,S==null?null:P[S],g,S),O=O==null?Ue:{_:O}),re.values[g]=O}function br(g,S,C){tf=Lt,nf=Ft,[Lt,Ft]=z.move(n,Lt,Ft),z.left=Lt,z.top=Ft,ve&&(ts&&_i(ts,jt(Lt),0,ee,ne),ns&&_i(ns,0,jt(Ft),ee,ne));let P,O=G>xe;bi=wt,$i=null;let X=I.ori==0?ee:ne,oe=I.ori==1?ee:ne;if(Lt<0||K==0||O){P=z.idx=null;for(let de=0;de<x.length;de++){let _e=wn[de];_e!=null&&_i(_e,-10,-10,ee,ne)}ln&&di(null,os,!0,g==null&&Wt.setSeries),re.live&&(ae.fill(P),F=!0)}else{let de,_e,we;r==1&&(de=I.ori==0?Lt:Ft,_e=pi(de,b),P=z.idx=ci(_e,e[0],G,xe),we=J(e[0][P],I,X,0));let Re=-10,Pe=-10,et=0,_t=0,ht=!0,lt="",$e="";for(let ze=r==2?1:0;ze<x.length;ze++){let Dt=x[ze],Ht=ae[ze],sn=Ht==null?null:r==1?e[ze][Ht]:e[ze][1][Ht],Et=z.dataIdx(n,ze,P,_e),Gt=Et==null?null:r==1?e[ze][Et]:e[ze][1][Et];if(F=F||Gt!=sn||Et!=Ht,ae[ze]=Et,ze>0&&Dt.show){let Un=Et==null?-10:Et==P?we:J(r==1?e[0][Et]:e[ze][0][Et],I,X,0),gn=Gt==null?-10:N(Gt,r==1?y[Dt.scale]:y[Dt.facets[1].scale],oe,0);if(ln&&Gt!=null){let Xn=I.ori==1?Lt:Ft,ni=$t(gt.dist(n,ze,Et,gn,Xn));if(ni<bi){let mi=gt.bias;if(mi!=0){let In=pi(Xn,Dt.scale),qn=Gt>=0?1:-1,ii=In>=0?1:-1;ii==qn&&(ii==1?mi==1?Gt>=In:Gt<=In:mi==1?Gt<=In:Gt>=In)&&(bi=ni,$i=ze)}else bi=ni,$i=ze}}if(F||Si){let Xn,ni;I.ori==0?(Xn=Un,ni=gn):(Xn=gn,ni=Un);let mi,In,qn,ii,gi,_n,Nn=!0,Ar=je.bbox;if(Ar!=null){Nn=!1;let vn=Ar(n,ze);qn=vn.left,ii=vn.top,mi=vn.width,In=vn.height}else qn=Xn,ii=ni,mi=In=je.size(n,ze);if(_n=je.fill(n,ze),gi=je.stroke(n,ze),Si)ze==$i&&bi<=gt.prox&&(Re=qn,Pe=ii,et=mi,_t=In,ht=Nn,lt=_n,$e=gi);else{let vn=wn[ze];vn!=null&&(ti[ze]=qn,yi[ze]=ii,hd(vn,mi,In,Nn),ud(vn,_n,gi),_i(vn,$n(qn),$n(ii),ee,ne))}}}}if(Si){let ze=gt.prox,Dt=Tr==null?bi<=ze:bi>ze||$i!=Tr;if(F||Dt){let Ht=wn[0];Ht!=null&&(ti[0]=Re,yi[0]=Pe,hd(Ht,et,_t,ht),ud(Ht,lt,$e),_i(Ht,$n(Re),$n(Pe),ee,ne))}}}if(Pt.show&&Yi)if(g!=null){let[de,_e]=Wt.scales,[we,Re]=Wt.match,[Pe,et]=g.cursor.sync.scales,_t=g.cursor.drag;if(tn=_t._x,nn=_t._y,tn||nn){let{left:ht,top:lt,width:$e,height:ze}=g.select,Dt=g.scales[Pe].ori,Ht=g.posToVal,sn,Et,Gt,Un,gn,Xn=de!=null&&we(de,Pe),ni=_e!=null&&Re(_e,et);Xn&&tn?(Dt==0?(sn=ht,Et=$e):(sn=lt,Et=ze),Gt=y[de],Un=J(Ht(sn,Pe),Gt,X,0),gn=J(Ht(sn+Et,Pe),Gt,X,0),so(hi(Un,gn),$t(gn-Un))):so(0,X),ni&&nn?(Dt==1?(sn=ht,Et=$e):(sn=lt,Et=ze),Gt=y[_e],Un=N(Ht(sn,et),Gt,oe,0),gn=N(Ht(sn+Et,et),Gt,oe,0),oo(hi(Un,gn),$t(gn-Un))):oo(0,oe)}else Ul()}else{let de=$t(tf-Qu),_e=$t(nf-ef);if(I.ori==1){let et=de;de=_e,_e=et}tn=un.x&&de>=un.dist,nn=un.y&&_e>=un.dist;let we=un.uni;we!=null?tn&&nn&&(tn=de>=we,nn=_e>=we,!tn&&!nn&&(_e>de?nn=!0:tn=!0)):un.x&&un.y&&(tn||nn)&&(tn=nn=!0);let Re,Pe;tn&&(I.ori==0?(Re=is,Pe=Lt):(Re=rs,Pe=Ft),so(hi(Re,Pe),$t(Pe-Re)),nn||oo(0,oe)),nn&&(I.ori==1?(Re=is,Pe=Lt):(Re=rs,Pe=Ft),oo(hi(Re,Pe),$t(Pe-Re)),tn||so(0,X)),!tn&&!nn&&(so(0,0),oo(0,0))}if(un._x=tn,un._y=nn,g==null){if(C){if(gf!=null){let[de,_e]=Wt.scales;Wt.values[0]=de!=null?pi(I.ori==0?Lt:Ft,de):null,Wt.values[1]=_e!=null?pi(I.ori==1?Lt:Ft,_e):null}lo(_c,n,Lt,Ft,ee,ne,P)}if(ln){let de=C&&Wt.setSeries,_e=gt.prox;Tr==null?bi<=_e&&di($i,os,!0,de):bi>_e?di(null,os,!0,de):$i!=Tr&&di($i,os,!0,de)}}F&&(re.idx=P,Ll()),S!==!1&&rn("setCursor")}let Ki=null;Object.defineProperty(n,"rect",{get(){return Ki==null&&ao(!1),Ki}});function ao(g=!1){g?Ki=null:(Ki=v.getBoundingClientRect(),rn("syncRect",Ki))}function of(g,S,C,P,O,X,oe){z._lock||Yi&&g!=null&&g.movementX==0&&g.movementY==0||(Pl(g,S,C,P,O,X,oe,!1,g!=null),g!=null?br(null,!0,!0):br(S,!0,!1))}function Pl(g,S,C,P,O,X,oe,de,_e){if(Ki==null&&ao(!1),St(g),g!=null)C=g.clientX-Ki.left,P=g.clientY-Ki.top;else{if(C<0||P<0){Lt=-10,Ft=-10;return}let[we,Re]=Wt.scales,Pe=S.cursor.sync,[et,_t]=Pe.values,[ht,lt]=Pe.scales,[$e,ze]=Wt.match,Dt=S.axes[0].side%2==1,Ht=I.ori==0?ee:ne,sn=I.ori==1?ee:ne,Et=Dt?X:O,Gt=Dt?O:X,Un=Dt?P:C,gn=Dt?C:P;if(ht!=null?C=$e(we,ht)?a(et,y[we],Ht,0):-10:C=Ht*(Un/Et),lt!=null?P=ze(Re,lt)?a(_t,y[Re],sn,0):-10:P=sn*(gn/Gt),I.ori==1){let Xn=C;C=P,P=Xn}}_e&&(S==null||S.cursor.event.type==_c)&&((C<=1||C>=ee-1)&&(C=Ir(C,ee)),(P<=1||P>=ne-1)&&(P=Ir(P,ne))),de?(Qu=C,ef=P,[is,rs]=z.move(n,C,P)):(Lt=C,Ft=P)}const Dl={width:0,height:0,left:0,top:0};function Ul(){ta(Dl,!1)}let af,lf,cf,uf;function ff(g,S,C,P,O,X,oe){Yi=!0,tn=nn=un._x=un._y=!1,Pl(g,S,C,P,O,X,oe,!0,!1),g!=null&&(E(vc,ou,hf,!1),lo(id,n,is,rs,ee,ne,null));let{left:de,top:_e,width:we,height:Re}=Pt;af=de,lf=_e,cf=we,uf=Re}function hf(g,S,C,P,O,X,oe){Yi=un._x=un._y=!1,Pl(g,S,C,P,O,X,oe,!1,!0);let{left:de,top:_e,width:we,height:Re}=Pt,Pe=we>0||Re>0,et=af!=de||lf!=_e||cf!=we||uf!=Re;if(Pe&&et&&ta(Pt),un.setScale&&Pe&&et){let _t=de,ht=we,lt=_e,$e=Re;if(I.ori==1&&(_t=_e,ht=Re,lt=de,$e=we),tn&&ji(b,pi(_t,b),pi(_t+ht,b)),nn)for(let ze in y){let Dt=y[ze];ze!=b&&Dt.from==null&&Dt.min!=wt&&ji(ze,pi(lt+$e,ze),pi(lt,ze))}Ul()}else z.lock&&(z._lock=!z._lock,br(S,!0,g!=null));g!=null&&($(vc,ou),lo(vc,n,Lt,Ft,ee,ne,null))}function Xm(g,S,C,P,O,X,oe){if(z._lock)return;St(g);let de=Yi;if(Yi){let _e=!0,we=!0,Re=10,Pe,et;I.ori==0?(Pe=tn,et=nn):(Pe=nn,et=tn),Pe&&et&&(_e=Lt<=Re||Lt>=ee-Re,we=Ft<=Re||Ft>=ne-Re),Pe&&_e&&(Lt=Lt<is?0:ee),et&&we&&(Ft=Ft<rs?0:ne),br(null,!0,!0),Yi=!1}Lt=-10,Ft=-10,ae.fill(null),br(null,!0,!0),de&&(Yi=de)}function df(g,S,C,P,O,X,oe){z._lock||(St(g),Je(),Ul(),g!=null&&lo(od,n,Lt,Ft,ee,ne,null))}function pf(){_.forEach(gE),me(n.width,n.height,!0)}Vr(Qa,Bs,pf);const as={};as.mousedown=ff,as.mousemove=of,as.mouseup=hf,as.dblclick=df,as.setSeries=(g,S,C,P)=>{let O=Wt.match[2];C=O(n,S,C),C!=-1&&di(C,P,!0,!1)},ve&&(E(id,v,ff),E(_c,v,of),E(rd,v,g=>{St(g),ao(!1)}),E(sd,v,Xm),E(od,v,df),pu.add(n),n.syncRect=ao);const na=n.hooks=i.hooks||{};function rn(g,S,C){Al?ro.push([g,S,C]):g in na&&na[g].forEach(P=>{P.call(null,n,S,C)})}(i.plugins||[]).forEach(g=>{for(let S in g.hooks)na[S]=(na[S]||[]).concat(g.hooks[S])});const mf=(g,S,C)=>C,Wt=qt({key:null,setSeries:!1,filters:{pub:_d,sub:_d},scales:[b,x[1]?x[1].scale:null],match:[vd,vd,mf],values:[null,null]},z.sync);Wt.match.length==2&&Wt.match.push(mf),z.sync=Wt;const gf=Wt.key,Il=am(gf);function lo(g,S,C,P,O,X,oe){Wt.filters.pub(g,S,C,P,O,X,oe)&&Il.pub(g,S,C,P,O,X,oe)}Il.sub(n);function qm(g,S,C,P,O,X,oe){Wt.filters.sub(g,S,C,P,O,X,oe)&&as[g](null,S,C,P,O,X,oe)}n.pub=qm;function Ym(){Il.unsub(n),pu.delete(n),L.clear(),cu(Qa,Bs,pf),c.remove(),ge==null||ge.remove(),rn("destroy")}n.destroy=Ym;function Nl(){rn("init",i,e),tt(e||i.data,!1),B[b]?wl(b,B[b]):Je(),he=Pt.show&&(Pt.width>0||Pt.height>0),Ae=F=!0,me(i.width,i.height)}return x.forEach(to),_.forEach(El),t?t instanceof HTMLElement?(t.appendChild(c),Nl()):t(n,Nl):Nl(),n}Kt.assign=qt;Kt.fmtNum=Uu;Kt.rangeNum=el;Kt.rangeLog=dl;Kt.rangeAsinh=Pu;Kt.orient=Kr;Kt.pxRatio=vt;Kt.join=ay;Kt.fmtDate=Nu,Kt.tzDate=vy;Kt.sync=am;{Kt.addGap=eE,Kt.clipGaps=gl;let i=Kt.paths={points:dm};i.linear=mm,i.stepped=iE,i.bars=rE,i.spline=oE}const _E=document.getElementById("app"),ei=new wp({antialias:!0,logarithmicDepthBuffer:!0});ei.setPixelRatio(Math.min(window.devicePixelRatio,2));ei.setSize(window.innerWidth,window.innerHeight);ei.shadowMap.enabled=!1;_E.appendChild(ei.domElement);const qo=new nS;qo.background=new ft(1118481);const hn=new Jn(60,window.innerWidth/window.innerHeight,.01,2e3);hn.position.set(3,3,3);const pt=new xS(hn,ei.domElement);pt.minPolarAngle=1e-4;pt.maxPolarAngle=Math.PI-1e-4;pt.target.set(0,0,0);pt.update();qo.add(new mS(16777215,.6));const xm=new pS(16777215,.6);xm.position.set(3,5,2);qo.add(xm);const mn=new To;qo.add(mn);const vE=new _S(.5);mn.add(vE);const xE=new MS;let kn=null;function ME(){kn&&(mn.remove(kn),kn.geometry.dispose(),kn.material.dispose(),kn=null)}function SE(i){i.computeBoundingBox();const e=i.boundingBox;if(!e)return;const t=new k;e.getSize(t);const n=Math.max(t.x,t.y,t.z)*.5,r=Math.max(1,n*2.5);hn.position.set(r,r,r),hn.far=Math.max(2e3,n*20),hn.updateProjectionMatrix(),pt.target.set(0,0,0),pt.update(),ym.copy(hn.position),Em.copy(pt.target)}function yE(i){const e=URL.createObjectURL(i);xE.load(e,t=>{URL.revokeObjectURL(e),ME();const n=!!t.getAttribute("color");t.computeBoundingBox();const r=t.boundingBox;if(r){const l=new k;r.getCenter(l),t.translate(-l.x,-l.y,-l.z)}let s=1;if(r){const l=new k;r.getSize(l),s=Math.max(l.x,l.y,l.z)*.5}const o=Math.max(.001,s*.003),a=new Tu({size:o,vertexColors:n,sizeAttenuation:!0,depthWrite:!1});kn=new Pp(t,a),kn.frustumCulled=!1,mn.add(kn),SE(t)},void 0,()=>{URL.revokeObjectURL(e)})}const EE=1145848656,TE=1179468099,Hn=new Map;let Bo=!1;const Ec=document.getElementById("camera-feed"),Tc=document.getElementById("camera-panel"),kd=document.getElementById("camera-toggle");let xo=null,bc=!1;var jd;Tc&&kd&&((jd=document.getElementById("camera-header"))==null||jd.addEventListener("click",()=>{Tc.classList.toggle("collapsed"),kd.textContent=Tc.classList.contains("collapsed")?"+":"—"}));const Ac=document.getElementById("ui"),wc=document.getElementById("ui-toggle-btn");Ac&&wc&&wc.addEventListener("click",()=>{Ac.classList.toggle("collapsed"),wc.textContent=Ac.classList.contains("collapsed")?"Controls +":"Controls -"});function bE(i){if(!Ec||bc)return;bc=!0;const t=new DataView(i).getUint32(4,!0),n=new Uint8Array(i,8,t);xo&&URL.revokeObjectURL(xo),xo=URL.createObjectURL(new Blob([n],{type:"image/jpeg"})),requestAnimationFrame(()=>{Ec&&xo&&(Ec.src=xo),bc=!1})}let Gu=0,js=0;function Mm(i){const e=new Bt;return e.set(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14],i[15]),e}function AE(i){const e=new DataView(i),t=new Uint8Array(i),n=e.getUint32(0,!0);if(n!==EE)return console.warn("[ws] Invalid mesh_create magic:",n.toString(16)),null;const r=e.getUint16(4,!0),s=e.getUint32(6,!0);let o=10;const a=t.slice(o,o+r),l=new TextDecoder().decode(a);o+=r;const c=s*3*4,u=t.slice(o,o+c),f=new Float32Array(u.buffer,u.byteOffset,s*3);o+=c;const d=s*3,m=t.slice(o,o+d);o+=d;const v=e.getUint8(o);o+=1;let M=null;if(v){M=[];for(let p=0;p<16;p++)M.push(e.getFloat32(o+p*4,!0))}return{meshId:l,positions:f,colors:m,pose:M}}function wE(i,e,t,n){let r=Hn.get(i);if(!r){const o=new An,a=new Tu({size:.008,vertexColors:!0,sizeAttenuation:!0});r=new Pp(o,a),r.frustumCulled=!1,r.matrixAutoUpdate=!1,mn.add(r),Hn.set(i,r)}r.geometry.setAttribute("position",new Gn(e,3));const s=new Float32Array(t.length);for(let o=0;o<t.length;o++)s[o]=t[o]/255;r.geometry.setAttribute("color",new Gn(s,3)),r.geometry.computeBoundingSphere(),js=0;for(const o of Hn.values()){const a=o.geometry.getAttribute("position");a&&(js+=a.count)}if(n){const o=Mm(n);r.matrix.copy(o),Hn.size<=5&&console.log(`[debug-mesh] ${i} pose translation: [${n[3].toFixed(3)}, ${n[7].toFixed(3)}, ${n[11].toFixed(3)}]`)}}function RE(i,e){const t=Hn.get(i);if(!t){console.warn(`[ws] Pose update for unknown mesh: ${i}`);return}const n=Mm(e);t.matrix.copy(n),Gu++}function CE(i){const e=Hn.get(i);if(e){mn.remove(e),e.geometry.dispose(),e.material.dispose(),Hn.delete(i),js=0;for(const t of Hn.values()){const n=t.geometry.getAttribute("position");n&&(js+=n.count)}}}function Yo(){for(const[,i]of Hn)mn.remove(i),i.geometry.dispose(),i.material.dispose();Hn.clear(),Gu=0,js=0,Ni()}let yn=null,Vu=!1;function Wu(){const e=`${location.protocol==="https:"?"wss:":"ws:"}//${location.host}/ws`;yn=new WebSocket(e),yn.binaryType="arraybuffer",yn.onopen=()=>{Bo=!0,console.log("[ws] Connected to demo server"),Ni(),sl()},yn.onclose=()=>{Bo=!1,yn=null,console.log("[ws] Disconnected"),Ni(),sl(),Vu||(console.log("[ws] Auto-reconnecting in 2s..."),setTimeout(Wu,2e3))},yn.onerror=()=>{},yn.onmessage=t=>{if(t.data instanceof ArrayBuffer){if(t.data.byteLength>=4)if(new DataView(t.data).getUint32(0,!0)===TE)bE(t.data);else{const r=AE(t.data);r&&(wE(r.meshId,r.positions,r.colors,r.pose),Ni())}}else try{const n=JSON.parse(t.data);n.type==="mesh_update_pose"?(RE(n.mesh_id,n.pose),Ni()):n.type==="mesh_delete"?(CE(n.mesh_id),Ni()):n.type==="clear"?Yo():n.type==="stats"?console.log("[ws] Server stats:",n):n.type==="objects_update"?(bn=n.objects||[],bn.length>0&&bn.filter(s=>s.label_scores&&Object.keys(s.label_scores).length>0).length===0&&console.warn("[ws] Objects received but none have label_scores - are you running the embedded RTSM visualization server?"),Mr(),Zr(),Ni()):n.type==="runtime_analytics"&&OE(n)}catch{}}}function LE(i){yn&&yn.readyState===WebSocket.OPEN&&yn.send(JSON.stringify({cmd:i}))}const Na=new Map,Fa=new Map;let bn=[],Xa=!0,Ro=!1,ki=new Map,zs=!1,Di=null,ai=null;const PE=.18;function Sm(i){const e=i.label_primary||i.label_hint;if(e&&e!=="unknown")return e;if(i.label_scores){let t="",n=0;for(const[r,s]of Object.entries(i.label_scores))r!=="unknown"&&s>n&&s>=PE&&(t=r,n=s);if(t)return t}return i.id.slice(0,8)}function gu(i,e="#ffffff"){const t=document.createElement("canvas"),n=t.getContext("2d");t.width=256,t.height=64,n.fillStyle="rgba(0,0,0,0.6)",n.fillRect(0,0,t.width,t.height),n.font="bold 24px system-ui, Arial",n.fillStyle=e,n.textAlign="center",n.textBaseline="middle",n.fillText(i,t.width/2,t.height/2);const r=new aS(t),s=new Rp({map:r,transparent:!0}),o=new rS(s);return o.scale.set(.5,.125,1),o}function Mr(){var e;for(const[t,n]of Na)if(!bn.find(r=>r.id===t)){mn.remove(n),n.geometry.dispose(),n.material.dispose(),Na.delete(t);const r=Fa.get(t);r&&(mn.remove(r),(e=r.material.map)==null||e.dispose(),r.material.dispose(),Fa.delete(t))}const i=bn.filter(t=>t.xyz_world).length;if(i>0&&i<=5)for(const t of bn.slice(0,3))t.xyz_world&&console.log(`[debug-obj] ${t.id.slice(0,8)} xyz: [${t.xyz_world[0].toFixed(3)}, ${t.xyz_world[1].toFixed(3)}, ${t.xyz_world[2].toFixed(3)}]`);for(const t of bn){if(!t.xyz_world)continue;let n=Na.get(t.id);if(!n){const l=new Au(.03,16,16),c=new ul({color:t.confirmed?65416:16755200,transparent:!0,opacity:.8});n=new Mi(l,c),n.renderOrder=999,mn.add(n),Na.set(t.id,n)}n.position.set(t.xyz_world[0],t.xyz_world[1],t.xyz_world[2]);const r=!zs||ki.has(t.id),s=Xa&&(!Ro||t.confirmed)&&r;n.visible=s,n.material.color.setHex(t.confirmed?65416:16755200),t.id===Wr?n.scale.set(1.8,1.8,1.8):n.scale.set(1,1,1);let o=Fa.get(t.id);const a=t.id.slice(0,8);o||(o=gu(a,t.confirmed?"#00ff88":"#ffaa00"),mn.add(o),Fa.set(t.id,o)),o.position.set(t.xyz_world[0],t.xyz_world[1]+.08,t.xyz_world[2]),o.visible=s}DE()}function DE(){var n;const i=Wr?bn.find(r=>r.id===Wr):null;if(!i||!i.xyz_world){Di&&(Di.visible=!1),ai&&(ai.visible=!1);return}if(!Di){const r=new bu(.06,.08,32),s=new ul({color:2003199,transparent:!0,opacity:.9,side:xi,depthTest:!1,depthWrite:!1});Di=new Mi(r,s),Di.renderOrder=1e3,mn.add(Di)}ai||(ai=gu("","#1e90ff"),ai.renderOrder=1001,mn.add(ai)),Di.position.set(i.xyz_world[0],i.xyz_world[1],i.xyz_world[2]),Di.lookAt(hn.position),Di.visible=!0;const e=i.id.slice(0,8),t=gu(`▶ ${e}`,"#1e90ff");t.material.depthTest=!1,t.material.depthWrite=!1,t.position.set(i.xyz_world[0],i.xyz_world[1]+.12,i.xyz_world[2]),t.renderOrder=1001,t.visible=!0,ai&&(mn.remove(ai),(n=ai.material.map)==null||n.dispose(),ai.material.dispose()),mn.add(t),ai=t}function Ni(){const i=document.getElementById("hud");if(!i)return;const e=bn.filter(t=>t.confirmed).length;i.innerHTML=["<b>RTSM Demo</b>",`WS: ${Bo?'<span style="color:#0f0">connected</span>':'<span style="color:#f55">disconnected</span>'}`,`Meshes: ${Hn.size} | Points: ${js.toLocaleString()}`,`Pose updates: ${Gu}`,`Objects: ${bn.length} (${e} confirmed)`].join("<br>")}const Rc=document.getElementById("file"),Cc=document.getElementById("load"),Lc=document.getElementById("reset"),Pc=document.getElementById("flipX"),Dc=document.getElementById("flipY"),Uc=document.getElementById("flipZ"),Oa=document.getElementById("toggleObj"),Ic=document.getElementById("filterConfirmed"),Nc=document.getElementById("clearStream"),Fc=document.getElementById("savePly"),Oc=document.getElementById("rebuild"),Uo=document.getElementById("disconnect"),Io=document.getElementById("reconnect"),Hd=document.getElementById("mode"),Pr=document.getElementById("rtsmReset"),Dr=document.getElementById("rtsmStats"),Bc=document.getElementById("object-panel"),zc=document.getElementById("panel-title"),fr=document.getElementById("object-search"),Mo=document.getElementById("panel-filter"),So=document.getElementById("panel-toggle"),kc=document.getElementById("object-list");let Ba=!1,Xu="",Wr=null,Is=!1;const hr=document.getElementById("snapshot-gallery"),Hc=document.getElementById("gallery-close"),dr=document.getElementById("gallery-images"),pr=document.getElementById("gallery-preview"),Gd=document.getElementById("gallery-info"),Bn=document.getElementById("gallery-loading"),Vd=document.getElementById("gallery-title"),Bi=document.getElementById("ss-rotate");Bi==null||Bi.addEventListener("change",()=>{const i=`rotate(${Bi.value}deg)`;pr&&(pr.style.transform=i),dr==null||dr.querySelectorAll(".gallery-thumb").forEach(e=>{e.style.transform=i})});let Co=[];function Ns(i){Hd&&(Hd.textContent=`Mode: ${i}`)}Ns("Free");const ym=hn.position.clone(),Em=pt.target.clone();let nl=!1,il=!1,rl=!1;function jo(){mn.scale.set(nl?-1:1,il?-1:1,rl?-1:1)}Lc==null||Lc.addEventListener("click",()=>{hn.position.copy(ym),hn.up.set(0,1,0),pt.target.copy(Em),nl=il=rl=!1,jo(),pt.update(),Ns("Free")});Pc==null||Pc.addEventListener("click",()=>{nl=!nl,jo()});Dc==null||Dc.addEventListener("click",()=>{il=!il,jo()});Uc==null||Uc.addEventListener("click",()=>{rl=!rl,jo()});Cc==null||Cc.addEventListener("click",()=>{var e;const i=(e=Rc==null?void 0:Rc.files)==null?void 0:e[0];i&&yE(i)});Oa==null||Oa.addEventListener("click",()=>{Xa=!Xa,Mr(),Oa.textContent=Xa?"Hide Objects":"Show Objects"});Ic?Ic.addEventListener("click",()=>{Ro=!Ro,console.log("[demo] Filter toggled, showOnlyConfirmed:",Ro),Mr(),Ic.textContent=Ro?"Confirmed Only":"All"}):console.warn("[demo] filterConfirmedBtn not found");So==null||So.addEventListener("click",()=>{Ba=!Ba,Bc==null||Bc.classList.toggle("collapsed",Ba),So&&(So.textContent=Ba?"▲":"▼")});Mo==null||Mo.addEventListener("click",()=>{Is=!Is,Mo.textContent=Is?"Confirmed":"All",Mo.classList.toggle("active",Is),Zr()});const Gc=document.getElementById("search-btn"),Vc=document.getElementById("show-all-btn");async function Tm(){const i=fr==null?void 0:fr.value.trim();if(!i){console.log("[semantic-search] Empty query, showing all objects"),bm();return}Xu=i,console.log(`[semantic-search] Searching for: "${i}"`);try{const t=await(await fetch(`${Ml}/search/semantic?query=${encodeURIComponent(i)}&top_k=5&threshold=0.10`)).json();if(console.log("[semantic-search] API response:",t),ki.clear(),t.results)for(const n of t.results)ki.set(n.id,n.score);zs=!0,Zr(),Mr(),console.log(`[semantic-search] Found ${ki.size} matches`)}catch(e){console.error("[semantic-search] API call failed:",e),alert("Semantic search failed. Is RTSM running?")}}function bm(){Xu="",ki.clear(),zs=!1,fr&&(fr.value=""),Zr(),Mr()}Gc==null||Gc.addEventListener("click",Tm);Vc==null||Vc.addEventListener("click",bm);fr==null||fr.addEventListener("keydown",i=>{i.key==="Enter"&&(i.preventDefault(),Tm())});function Zr(){if(!kc)return;let i;if(zs?(i=bn.filter(e=>Is&&!e.confirmed?!1:ki.has(e.id)),i.sort((e,t)=>{const n=ki.get(e.id)||0;return(ki.get(t.id)||0)-n})):i=bn.filter(e=>!(Is&&!e.confirmed)),zc){const e=i.filter(t=>t.confirmed).length;zs?zc.textContent=`Search "${Xu}": ${i.length} matches`:zc.textContent=`Objects (${i.length}) — ${e} confirmed`}kc.innerHTML=i.map(e=>{const t=Sm(e),n=e.id===Wr,r=ki.get(e.id),s=zs&&r!==void 0?`sim: ${r.toFixed(2)}`:`stab: ${e.stability.toFixed(2)}`;return`
      <div class="object-item ${n?"selected":""}" data-id="${e.id}">
        <div class="object-dot ${e.confirmed?"confirmed":"proto"}"></div>
        <div class="object-info">
          <div class="object-label">${e.id.slice(0,8)}</div>
          <div class="object-meta">${t} · ${s}</div>
        </div>
      </div>
    `}).join(""),kc.querySelectorAll(".object-item").forEach(e=>{e.addEventListener("click",()=>{const t=e.getAttribute("data-id");t&&UE(t)})})}function UE(i){Wr===i?(Wr=null,hr==null||hr.classList.remove("visible")):(Wr=i,IE(i)),Zr(),Mr()}Hc==null||Hc.addEventListener("click",()=>{hr==null||hr.classList.remove("visible")});async function IE(i){if(!(!hr||!dr||!Bn)){if(hr.classList.add("visible"),dr.innerHTML="",pr==null||pr.classList.remove("visible"),Bn&&(Bn.style.display="block",Bn.textContent="Loading snapshots..."),Vd){const e=bn.find(n=>n.id===i),t=e?Sm(e):i.slice(0,8);Vd.textContent=`Snapshots: ${t}`}try{const t=await(await fetch(`${Ml}/objects/${i}/snapshots`)).json();if(t.error){Bn&&(Bn.textContent=`Error: ${t.error}`);return}if(Co=t.snapshots||[],Co.length===0){Bn&&(Bn.textContent="No snapshots available");return}Bn&&(Bn.style.display="none"),Co.forEach((n,r)=>{const s=document.createElement("img");s.className="gallery-thumb"+(r===0?" selected":""),s.src=n.data,Bi!=null&&Bi.value&&Bi.value!=="0"&&(s.style.transform=`rotate(${Bi.value}deg)`),s.alt=`Snapshot ${r+1}`,s.dataset.index=String(r),s.addEventListener("click",()=>Wd(r)),dr.appendChild(s)}),Wd(0),Gd&&(Gd.textContent=`${Co.length} snapshot(s) | Most recent first`)}catch(e){console.error("[gallery] Failed to load snapshots:",e),Bn&&(Bn.style.display="block",Bn.textContent="Failed to load snapshots")}}}function Wd(i){if(!dr||!pr)return;dr.querySelectorAll(".gallery-thumb").forEach((t,n)=>{t.classList.toggle("selected",n===i)});const e=Co[i];e&&(pr.src=e.data,pr.classList.add("visible"))}Nc==null||Nc.addEventListener("click",()=>{LE("clear"),Yo()});Oc==null||Oc.addEventListener("click",()=>{Yo(),yn&&yn.close()});function sl(){Uo&&(Uo.disabled=!Bo),Io&&(Io.disabled=Bo)}Uo==null||Uo.addEventListener("click",()=>{Vu=!0,Yo(),bn=[],Mr(),Zr(),yn&&(yn.close(),yn=null),sl()});Io==null||Io.addEventListener("click",()=>{Vu=!1,Wu()});const Ml="";Pr==null||Pr.addEventListener("click",async()=>{var i,e,t,n,r,s;if(confirm("Reset RTSM? This will clear all objects, keyframes, and sweep state.")){Pr.disabled=!0,Pr.textContent="Resetting...";try{const a=await(await fetch(`${Ml}/reset`,{method:"POST"})).json();console.log("[RTSM] Reset result:",a),Yo(),bn=[],Mr(),Zr(),Ni(),alert(`RTSM Reset Complete!

Cleared:
- ${((e=(i=a.cleared)==null?void 0:i.working_memory)==null?void 0:e.objects_cleared)||0} objects
- ${((n=(t=a.cleared)==null?void 0:t.sweep_cache)==null?void 0:n.view_states_cleared)||0} sweep states
- ${((s=(r=a.cleared)==null?void 0:r.visualization)==null?void 0:s.keyframes_cleared)||0} keyframes`)}catch(o){console.error("[RTSM] Reset failed:",o),alert("Failed to reset RTSM. Is the API server running?")}finally{Pr.disabled=!1,Pr.textContent="Reset WM"}}});Dr==null||Dr.addEventListener("click",async()=>{Dr.disabled=!0,Dr.textContent="Loading...";try{const e=await(await fetch(`${Ml}/stats/detailed`)).json();console.log("[RTSM] Stats:",e);const t=e.working_memory||{},n=e.sweep_cache||{},r=e.frame_window||{},s=e.visualization||{};alert(["RTSM Statistics","═══════════════════════","","Working Memory:",`  Objects: ${t.objects||0} (${t.confirmed||0} confirmed)`,`  Avg Hits: ${(t.avg_hits||0).toFixed(1)}`,`  Upserts: ${t.upserts_total||0}`,"","Sweep Cache:",`  Cells: ${n.cells||0}`,`  View States: ${n.view_states||0}`,`  Cam Snapshots: ${n.cam_snapshots||0}`,"","Frame Buffer:",`  RGB Frames: ${r.rgb_frames||0}`,`  Depth Frames: ${r.depth_frames||0}`,"","Visualization:",`  Keyframes: ${s.keyframes||0}`,`  Total Points: ${(s.total_points||0).toLocaleString()}`].join(`
`))}catch(i){console.error("[RTSM] Stats fetch failed:",i),alert("Failed to fetch RTSM stats. Is the API server running?")}finally{Dr.disabled=!1,Dr.textContent="Stats"}});function NE(){const i=[],e=[],t=new Bt,n=new k;for(const r of Hn.values()){const s=r.geometry.getAttribute("position"),o=r.geometry.getAttribute("color");if(s){t.copy(r.matrix);for(let a=0;a<s.count;a++)n.fromBufferAttribute(s,a),n.applyMatrix4(t),i.push(n.x,n.y,n.z),o?e.push(o.getX(a),o.getY(a),o.getZ(a)):e.push(1,1,1)}}if(kn){const r=kn.geometry.getAttribute("position"),s=kn.geometry.getAttribute("color");if(r)for(let o=0;o<r.count;o++)n.fromBufferAttribute(r,o),i.push(n.x,n.y,n.z),s?e.push(s.getX(o),s.getY(o),s.getZ(o)):e.push(1,1,1)}return{positions:new Float32Array(i),colors:new Float32Array(e)}}function FE(i,e){const t=i.length/3,n=["ply","format ascii 1.0",`element vertex ${t}`,"property float x","property float y","property float z","property uchar red","property uchar green","property uchar blue","end_header"].join(`
`),r=[];for(let s=0;s<t;s++){const o=Math.round(e[s*3]*255),a=Math.round(e[s*3+1]*255),l=Math.round(e[s*3+2]*255);r.push(`${i[s*3]} ${i[s*3+1]} ${i[s*3+2]} ${o} ${a} ${l}`)}return n+`
`+r.join(`
`)+`
`}Fc==null||Fc.addEventListener("click",()=>{const{positions:i,colors:e}=NE();if(i.length===0){console.log("[demo] No points to export");return}const t=FE(i,e),n=new Blob([t],{type:"application/octet-stream"}),r=URL.createObjectURL(n),s=document.createElement("a");s.href=r,s.download="rtsm_pointcloud.ply",document.body.appendChild(s),s.click(),s.remove(),URL.revokeObjectURL(r),console.log(`[demo] Exported ${i.length/3} points`)});let zo=!1,ko=!1,Xi=!1,ol=0,qu=0,Yu=!1,ju=!1,$u=!1,Sl=!1;function Wc(i){if(i){const e=pt.getAzimuthalAngle();pt.minAzimuthAngle=e-1e-4,pt.maxAzimuthAngle=e+1e-4}else pt.minAzimuthAngle=-1/0,pt.maxAzimuthAngle=1/0}function Xc(i){if(i){const e=pt.getPolarAngle();pt.minPolarAngle=Math.max(0,e-1e-4),pt.maxPolarAngle=Math.min(Math.PI,e+1e-4)}else pt.minPolarAngle=1e-4,pt.maxPolarAngle=Math.PI-1e-4}function Vi(){if(Xi){Ns("Roll-only");return}zo&&!ko?(Xc(!1),Wc(!0),Ns("Pitch-only")):ko&&!zo?(Wc(!1),Xc(!0),Ns("Yaw-only")):(Wc(!1),Xc(!1),Ns("Free"))}function Ku(){zo=!1,ko=!1,Vi()}pt.addEventListener("start",()=>{Sl=!0});pt.addEventListener("end",()=>{Sl=!1,Ku()});ei.domElement.addEventListener("pointerdown",i=>{i.button===0&&(qu=i.clientX,$u?(Xi=!0,ol=i.clientX,pt.enableRotate=!1,Vi(),i.preventDefault()):ju?(ko=!0,Vi()):Yu&&(zo=!0,Vi()))},{capture:!0});ei.domElement.addEventListener("pointerup",i=>{i.button===0&&(Xi?(Xi=!1,pt.enableRotate=!0,Vi()):Ku())},{capture:!0});ei.domElement.addEventListener("pointermove",i=>{if(qu=i.clientX,!Xi)return;const e=i.clientX-ol;if(e!==0){const t=new k().subVectors(pt.target,hn.position).normalize(),n=new _r().setFromAxisAngle(t,e*.005);hn.up.applyQuaternion(n).normalize(),hn.lookAt(pt.target),ol=i.clientX}i.preventDefault()},{capture:!0});document.addEventListener("keydown",i=>{(i.key==="z"||i.key==="Z")&&(Yu=!0),(i.key==="x"||i.key==="X")&&(ju=!0),(i.key==="c"||i.key==="C")&&($u=!0),Sl&&(i.key==="c"||i.key==="C"?Xi||(Xi=!0,ol=qu,pt.enableRotate=!1,Vi()):i.key==="x"||i.key==="X"?(ko=!0,Vi()):(i.key==="z"||i.key==="Z")&&(zo=!0,Vi()))});document.addEventListener("keyup",i=>{(i.key==="z"||i.key==="Z")&&(Yu=!1),(i.key==="x"||i.key==="X")&&(ju=!1),(i.key==="c"||i.key==="C")&&($u=!1),Sl&&((i.key==="c"||i.key==="C")&&Xi?(Xi=!1,pt.enableRotate=!0,Vi()):(i.key==="x"||i.key==="X"||i.key==="z"||i.key==="Z")&&Ku())});const yo=new gS,qc=new qe;ei.domElement.addEventListener("dblclick",i=>{const e=ei.domElement.getBoundingClientRect();if(qc.x=(i.clientX-e.left)/e.width*2-1,qc.y=-((i.clientY-e.top)/e.height)*2+1,yo.setFromCamera(qc,hn),kn){yo.params.Points.threshold=.01;const t=yo.intersectObject(kn,!1);if(t.length>0){pt.target.copy(t[0].point),pt.update();return}}for(const t of Hn.values()){yo.params.Points.threshold=.01;const n=yo.intersectObject(t,!1);if(n.length>0){pt.target.copy(n[0].point),pt.update();return}}});function Am(){requestAnimationFrame(Am),ei.render(qo,hn)}window.addEventListener("resize",()=>{hn.aspect=window.innerWidth/window.innerHeight,hn.updateProjectionMatrix(),ei.setSize(window.innerWidth,window.innerHeight)});let Ho=!1,ct=[],Fi=[],xr={},Vt=null,$s=null,Ks=null,mr=null,za=!1;const Eo=document.getElementById("analytics-config-toggle");function Xd(i,e){const t=Date.now()/1e3-e;for(;i.length>0&&i[0].wall_ts<t;)i.shift()}function OE(i){var e,t,n,r,s,o;i.mode==="full"?(ct=((e=i.latency)==null?void 0:e.hourly)??[],Fi=((t=i.segmentation)==null?void 0:t.hourly)??[],i.config&&(Vt=i.config,Ho&&(wm(),Rm()))):i.mode==="append"&&((n=i.latency)!=null&&n.bucket&&(ct.push(i.latency.bucket),Xd(ct,3600)),(r=i.segmentation)!=null&&r.bucket&&(Fi.push(i.segmentation.bucket),Xd(Fi,3600))),xr={latency:(s=i.latency)==null?void 0:s.aggregate,segmentation:(o=i.segmentation)==null?void 0:o.aggregate},Ho&&Cm()}function BE(i){document.querySelectorAll("#tab-bar .tab-btn").forEach(n=>n.classList.toggle("active",n.dataset.tab===i));const e=document.getElementById("view-3d"),t=document.getElementById("view-analytics");i==="3d"?(e&&(e.style.display="block"),t&&(t.style.display="none"),Ho=!1):(e&&(e.style.display="none"),t&&(t.style.display="block"),Ho=!0,GE(),Vt&&(wm(),Rm()),Cm())}var $d;($d=document.getElementById("tab-bar"))==null||$d.addEventListener("click",i=>{const e=i.target.closest(".tab-btn");e!=null&&e.dataset.tab&&BE(e.dataset.tab)});Eo==null||Eo.addEventListener("click",()=>{za=!za;const i=document.getElementById("analytics-config");i&&(i.style.display=za?"none":""),Eo&&(Eo.textContent=za?"Config ▸":"Config ▾")});function wm(){var l,c;const i=document.getElementById("analytics-config");if(!i||!Vt)return;const e=Vt.segmentation||{},t=Vt.receiver||{},n=Vt.pipeline||{},r=e.fastsam||{},s=e.yoloe||{},o=(u,f,d)=>`<span class="config-item"><span class="config-key">${u}:</span> <span class="${d?"config-highlight":"config-val"}">${f}</span></span>`;let a=[o("backend",e.backend,!0),o("device",n.device??"?"),o("retina",e.retina_masks??"?")];if(e.backend==="dual")a.push(o("fastsam",`${r.imgsz}px conf=${r.conf} iou=${r.iou}`),o("yoloe",`${s.imgsz}px conf=${s.conf} iou=${s.iou}`),o("dual-iou",(l=e.dual)==null?void 0:l.iou_confirm_threshold),o("prefer",(c=e.dual)==null?void 0:c.prefer_mask));else{const u=e[e.backend]||{};a.push(o("imgsz",`${u.imgsz}px`),o("conf",u.conf),o("max-det",u.max_det))}a.push(o("kf-every",`${t.keyframe_every_n}f`),o("throttle",`${t.nonkf_min_interval_s}s`),o("queue",t.queue_maxsize),o("top-k",n.topk_preclip)),i.innerHTML=`<div class="config-grid">${a.join("")}</div>`}function Rm(){var t;const i=document.querySelector("#analytics-seg-section .chart-section-label");if(!i||!Vt)return;const e=(t=Vt.segmentation)==null?void 0:t.backend;e==="dual"?i.textContent="Segmentation (Dual Confirmation)":i.textContent=`Segmentation (${e} only)`}function Cm(){zE(),kE(),HE(),WE()}function Ui(i,e,t){const n=document.getElementById(i);if(!n)return;const r=n.querySelector(".kpi-value");r&&(r.textContent=e,r.className="kpi-value"+(t?" "+t:""))}function nr(i,e){const t=document.getElementById(i);if(!t)return;const n=t.querySelector(".kpi-sub");n&&(n.textContent=e)}function zE(){var n,r,s;const i=xr.latency,e=xr.segmentation,t=ct.length>0?ct[ct.length-1]:null;if(i){Ui("kpi-input-hz",`${i.input_hz??0}`),Ui("kpi-proc-hz",`${i.processing_hz??0}`),nr("kpi-proc-hz",`Hz (${((i.effective_ratio??0)*100).toFixed(0)}% ratio)`);const o=(n=i.t_total)!=null&&n.mean?(i.t_total.mean*1e3).toFixed(0):"—",a=(r=i.t_total)!=null&&r.p95?(i.t_total.p95*1e3).toFixed(0):"?",l=Number(o)>500?"yellow":Number(o)>1e3?"red":"";Ui("kpi-latency",o,l),nr("kpi-latency",`ms mean (p95: ${a}ms)`);const c=(t==null?void 0:t.queue_depth_max)??0,u=(t==null?void 0:t.queue_drops)??0,f=u>0||c>400?"red":c>256?"yellow":"green";Ui("kpi-queue",`${c}`,f),nr("kpi-queue",u>0?`/ 512 cap  (${u} drops!)`:"/ 512 cap");const d=document.getElementById("kpi-queue");d&&d.classList.toggle("congestion",u>0);const m=((i.mask_survival_rate??0)*100).toFixed(0);Ui("kpi-masks",`${i.mean_masks_in??0}`),nr("kpi-masks",`→ ${i.mean_candidates??0} selected (${m}%)`)}if(e){const o=e.backend??((s=Vt==null?void 0:Vt.segmentation)==null?void 0:s.backend)??"?";o==="dual"?(Ui("kpi-dual",`${((e.dual_rate??0)*100).toFixed(0)}%`,"green"),nr("kpi-dual",`dual | ${((e.fastsam_only_rate??0)*100).toFixed(0)}% fsam | ${((e.yoloe_only_rate??0)*100).toFixed(0)}% yoloe`)):(Ui("kpi-dual",`${e.mean_total??0}`),nr("kpi-dual",`masks/frame (${o})`))}if(ct.length>0){let o=t;for(let v=ct.length-1;v>=0;v--)if((ct[v].wm_total??0)>0||(ct[v].frames_in_bucket??0)>0){o=ct[v];break}const a=(o==null?void 0:o.wm_confirmed)??0,l=(o==null?void 0:o.wm_total)??0,c=(o==null?void 0:o.wm_proto)??0,u=a>0?"green":l>0?"yellow":"";Ui("kpi-objects",`${a}`,u),nr("kpi-objects",`confirmed / ${l} total (${c} proto)`);let f=0,d=0;for(const v of ct)f+=v.assoc_matched??0,d+=v.assoc_created??0;const m=f+d>0?(f/(f+d)*100).toFixed(0):"—";Ui("kpi-assoc",`${f}`,f>0?"green":""),nr("kpi-assoc",`matched / ${d} new (${m}% match rate)`)}}function kE(){var r;const i=document.getElementById("analytics-latency-breakdown");if(!i)return;const e=xr.latency;if(!e){i.innerHTML="";return}const t=((r=e.t_total)==null?void 0:r.mean)??0,n=[{name:"Seg",stats:e.t_segmentation,color:"#ff6b6b"},{name:"Heur",stats:e.t_heuristics,color:"#ffd93d"},{name:"Score",stats:e.t_scoring,color:"#aaaaaa"},{name:"CLIP",stats:e.t_clip,color:"#6bcb77"},{name:"Assoc",stats:e.t_association,color:"#4d96ff"}];i.innerHTML='<div class="latency-breakdown">'+n.map(s=>{var c;const o=((c=s.stats)==null?void 0:c.mean)??0,a=(o*1e3).toFixed(0),l=t>0?(o/t*100).toFixed(0):"0";return`<div class="latency-item">
      <span class="latency-dot" style="background:${s.color}"></span>
      <span class="latency-name">${s.name}</span>
      <span class="latency-val">${a}ms</span>
      <span class="latency-pct">(${l}%)</span>
    </div>`}).join("")+"</div>"}function HE(){var o,a,l;const i=xr.latency,e=xr.segmentation,t=ct.length>0?ct[ct.length-1]:null,n=document.getElementById("analytics-throughput-detail");if(n&&i){const c=(t==null?void 0:t.throttle_skips)??0,u=(t==null?void 0:t.gate_rejections)??0;n.textContent=`throttle: ${c}/s | gate: ${u}/s`}const r=document.getElementById("analytics-latency-detail");if(r&&i){const c=(o=i.t_total)!=null&&o.p95?(i.t_total.p95*1e3).toFixed(0):"?",u=(a=i.t_total)!=null&&a.max?(i.t_total.max*1e3).toFixed(0):"?";r.textContent=`p95: ${c}ms | max: ${u}ms`}const s=document.getElementById("analytics-seg-detail");s&&e&&((e.backend??((l=Vt==null?void 0:Vt.segmentation)==null?void 0:l.backend)??"?")==="dual"?s.textContent=`raw: FastSAM ${e.mean_fastsam_raw??0} | YOLOE ${e.mean_yoloe_raw??0} | survival: ${((e.staged_survival_rate??0)*100).toFixed(0)}%`:s.textContent=`${e.mean_total??0} masks/frame | survival: ${((e.staged_survival_rate??0)*100).toFixed(0)}%`)}const ka={stroke:"#555",grid:{stroke:"#222"}},Ha={stroke:"#555",grid:{stroke:"#222"},size:45};function zr(i){const e=document.getElementById(i);return e?Math.max(300,e.clientWidth):600}function GE(){var i;if(!$s){const e=document.getElementById("analytics-throughput-chart");e&&($s=new Kt({width:zr("analytics-throughput-chart"),height:150,series:[{},{label:"Input Hz",stroke:"#888",width:1},{label:"Proc Hz",stroke:"#1e90ff",width:2},{label:"Q Max",stroke:"#ffffff40",fill:"#ffffff10",width:1}],axes:[ka,Ha],cursor:{show:!0},legend:{show:!1}},[[],[],[],[]],e))}if(!Ks){const e=document.getElementById("analytics-latency-chart");e&&(Ks=new Kt({width:zr("analytics-latency-chart"),height:150,series:[{},{label:"Seg",stroke:"#ff6b6b",fill:"#ff6b6b40",width:1},{label:"Heur",stroke:"#ffd93d",fill:"#ffd93d40",width:1},{label:"Score",stroke:"#aaa",fill:"#aaaaaa30",width:1},{label:"CLIP",stroke:"#6bcb77",fill:"#6bcb7740",width:1},{label:"Assoc",stroke:"#4d96ff",fill:"#4d96ff40",width:1}],axes:[ka,Ha],cursor:{show:!0},legend:{show:!1}},[[],[],[],[],[],[]],e))}if(!mr){const e=document.getElementById("analytics-seg-chart");e&&(((i=Vt==null?void 0:Vt.segmentation)==null?void 0:i.backend)==="dual"?mr=new Kt({width:zr("analytics-seg-chart"),height:120,series:[{},{label:"Dual",stroke:"#00ff88",fill:"#00ff8840",width:1},{label:"FastSAM",stroke:"#1e90ff",fill:"#1e90ff40",width:1},{label:"YOLOE",stroke:"#ffaa00",fill:"#ffaa0040",width:1}],axes:[ka,Ha],cursor:{show:!0},legend:{show:!1}},[[],[],[],[]],e):mr=new Kt({width:zr("analytics-seg-chart"),height:120,series:[{},{label:"Masks",stroke:"#1e90ff",fill:"#1e90ff40",width:2}],axes:[ka,Ha],cursor:{show:!0},legend:{show:!1}},[[],[]],e))}}const VE=new ResizeObserver(()=>{Ho&&($s&&$s.setSize({width:zr("analytics-throughput-chart"),height:150}),Ks&&Ks.setSize({width:zr("analytics-latency-chart"),height:150}),mr&&mr.setSize({width:zr("analytics-seg-chart"),height:120}))}),qd=document.getElementById("analytics-content");qd&&VE.observe(qd);function Yd(i){if(i.length===0)return[];const e=[i[0].slice()];for(let t=1;t<i.length;t++)e.push(e[t-1].map((n,r)=>n+(i[t][r]??0)));return e}function WE(){var i;if($s&&ct.length>0&&$s.setData([ct.map(e=>e.wall_ts),ct.map(e=>e.input_hz??0),ct.map(e=>e.processing_hz??0),ct.map(e=>e.queue_depth_max??0)]),Ks&&ct.length>0){const e=ct.map(r=>r.wall_ts),t=[ct.map(r=>r.t_seg_ms??0),ct.map(r=>r.t_heur_ms??0),ct.map(r=>r.t_scoring_ms??0),ct.map(r=>r.t_clip_ms??0),ct.map(r=>r.t_assoc_ms??0)],n=Yd(t);Ks.setData([e,...n])}if(mr&&Fi.length>0){const e=Fi.map(n=>n.wall_ts);if(((i=Vt==null?void 0:Vt.segmentation)==null?void 0:i.backend)==="dual"){const n=[Fi.map(s=>s.dual_rate??0),Fi.map(s=>s.fastsam_only_rate??0),Fi.map(s=>s.yoloe_only_rate??0)],r=Yd(n);mr.setData([e,...r])}else mr.setData([e,Fi.map(n=>n.mean_total??0)])}}function XE(){var l,c;const i=new Date().toISOString().replace("T"," ").substring(0,19),e=xr.latency,t=xr.segmentation,n=Vt,r=((l=n==null?void 0:n.segmentation)==null?void 0:l.backend)??"unknown",s=((c=n==null?void 0:n.pipeline)==null?void 0:c.device)??"?",o=u=>u?`${(u.mean*1e3).toFixed(0)}ms / ${(u.p95*1e3).toFixed(0)}ms`:"?",a=[`RTSM Analytics Snapshot (${i})`,`Backend: ${r} | Device: ${s}`,"---"];if(e){const u=ct.length>0?ct[ct.length-1]:null;a.push(`Throughput: ${e.input_hz??0} Hz in -> ${e.processing_hz??0} Hz proc (${((e.effective_ratio??0)*100).toFixed(0)}%)`,`Queue: ${(u==null?void 0:u.queue_depth_mean)??0} avg / ${(u==null?void 0:u.queue_depth_max)??0} max / 512 cap | Drops: ${(u==null?void 0:u.queue_drops)??0}`,"---","Latency (mean / p95):",`  Total: ${o(e.t_total)}`,`  Seg: ${o(e.t_segmentation)} | Heur: ${o(e.t_heuristics)}`,`  Score: ${o(e.t_scoring)} | CLIP: ${o(e.t_clip)} | Assoc: ${o(e.t_association)}`)}if(t&&(a.push("---"),r==="dual"?a.push(`Segmentation: Dual ${((t.dual_rate??0)*100).toFixed(0)}% | FastSAM-only ${((t.fastsam_only_rate??0)*100).toFixed(0)}% | YOLOE-only ${((t.yoloe_only_rate??0)*100).toFixed(0)}%`,`Raw: FastSAM ${t.mean_fastsam_raw??0} avg | YOLOE ${t.mean_yoloe_raw??0} avg | Survival: ${((t.staged_survival_rate??0)*100).toFixed(0)}%`):a.push(`Segmentation (${r}): ${t.mean_total??0} masks/frame | Survival: ${((t.staged_survival_rate??0)*100).toFixed(0)}%`)),ct.length>0){let u={confirmed:0,total:0,proto:0};for(let m=ct.length-1;m>=0;m--)if((ct[m].wm_total??0)>0){u={confirmed:ct[m].wm_confirmed??0,total:ct[m].wm_total??0,proto:ct[m].wm_proto??0};break}let f=0,d=0;for(const m of ct)f+=m.assoc_matched??0,d+=m.assoc_created??0;a.push("---",`Objects: ${u.confirmed} confirmed / ${u.total} total (${u.proto} proto)`,`Association: ${f} matched / ${d} created`)}return a.join(`
`)}var Kd;(Kd=document.getElementById("analytics-copy"))==null||Kd.addEventListener("click",async()=>{const i=document.getElementById("analytics-copy"),e=XE();try{await navigator.clipboard.writeText(e),i&&(i.textContent="Copied!",i.classList.add("copied"),setTimeout(()=>{i.textContent="Copy Data",i.classList.remove("copied")},1500))}catch{const t=document.createElement("textarea");t.value=e,document.body.appendChild(t),t.select(),document.execCommand("copy"),document.body.removeChild(t),i&&(i.textContent="Copied!",i.classList.add("copied"),setTimeout(()=>{i.textContent="Copy Data",i.classList.remove("copied")},1500))}});Wu();Ni();sl();jo();Am();
