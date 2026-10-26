/* DOM interaction tests without a browser. Visual browser QA remains separate. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
class Element {
  constructor(tag='div'){this.tag=tag;this.children=[];this.value='';this.checked=false;this.events={};this.attributes={};this.textContent='';this.classList={add:()=>{}};this.hidden=false;}
  append(child){this.children.push(child);if(this.tag==='select'&&this.children.length===1)this.value=child.value;}
  replaceChildren(...children){this.children=children;}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(name,fn){this.events[name]=fn;}
}
const template=fs.readFileSync(path.join(__dirname,'../../assets/viewer.html'),'utf8');
const script=template.match(/<script>([\s\S]*?)<\/script>/)[1];
function execute(data){
 const nodes={};for(const id of ['data','project','sheet','state','search','raw','overlay','items','drawing','empty','detail','observations'])nodes[id]=new Element(id==='sheet'||id==='state'?'select':'div');
 nodes.data.textContent=JSON.stringify(data);nodes.state.value='all';
 const document={getElementById:id=>nodes[id],createElement:tag=>new Element(tag),createElementNS:(ns,tag)=>new Element(tag)};
 vm.runInNewContext(script,{document,JSON,Number,Set});return nodes;
}
const data={project:'SYNTHETIC',documents:[{id:'d',name:'SYNTHETIC.pdf',status:'indexed'}],pages:[{id:'p',document_id:'d',page:1,width:100,height:100,image:'images/p.png'}],references:[{id:'r',page_id:'p',kind:'path',bbox:[10,10,50,50],commands:[['l',[10,10],[50,50]]]}],quantities:[{id:'q',page_id:'p',description:'Known luminaire',source_refs:['r'],quantity:1,unit:'u',review_status:'confirmed'},{id:'pending',page_id:null,description:'Necessary boxes, unquantified',source_refs:[],quantity:null,unit:'u',review_status:'pending'}],observations:[]};
let nodes=execute(data);
assert.equal(nodes.items.children.length,2,'Pending items without a page must remain visible');
assert.equal(nodes.overlay.children.filter(x=>x.tag==='rect').length,1);
nodes.overlay.children[0].events.click();assert.match(nodes.detail.textContent,/'reference'|"reference"/);
nodes.state.value='pending';nodes.state.events.change();assert.equal(nodes.items.children.length,1);assert.match(nodes.items.children[0].textContent,/unquantified/);
nodes.search.value='does-not-exist';nodes.search.events.input();assert.match(nodes.items.children[0].textContent,/Sin partidas/);
nodes=execute({...data,pages:[],references:[],quantities:[data.quantities[1]]});
assert.equal(nodes.items.children.length,1,'No-plan projects must still list pending materials');assert.equal(nodes.empty.hidden,false);
console.log('Viewer DOM interactions: 8 assertions passed; no browser rendering claimed.');
