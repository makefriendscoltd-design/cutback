import React from 'react'; import {Composition,registerRoot} from 'remotion'; import {AutoEditor,Props} from './Composition'; import oren from '../../config/design_tokens.oren.json';
const Root:React.FC=()=> <Composition<Props> id="AutoEditor" component={AutoEditor} width={2160} height={3840} fps={30} durationInFrames={300} defaultProps={{style:'oren',scenes:[],captions:[],fps:30,tokens:oren}} calculateMetadata={({props})=>({durationInFrames:Math.max(1,Math.ceil((props.renderDuration||Math.max(...props.scenes.map(s=>s.end),1))*30)),props})}/>;
registerRoot(Root);
