import React from 'react'; import {FullscreenAsset,KeywordHighlight,Tokens} from './Common';
export const JackBigKeyword=KeywordHighlight; export const JackStoryMontage=FullscreenAsset; export const JackEvidenceOverlay=FullscreenAsset;
export const JackPatternInterrupt:React.FC<{scale:number;tokens:Tokens}>=({scale,tokens})=><div style={{position:'absolute',inset:0,border:`${Math.max(8,tokens.canvas.safeX*.25)*scale}px solid white`,mixBlendMode:'difference'}}/>;
