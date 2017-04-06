#SP2M v1.03d author 戴巍
#http://weibo.com/david376

############################################################################################
#重要。目前版本针对vray和arnold可以结合各种maya版本使用。
#针对redshfit只测试了2016版本的maya，别的版本目测会有问题，遇到问题请联系我，持续修改升级。这就是个苦力活

#感谢之前一直帮忙测试，提供bug的朋友，因为你们，这个工具变得更好更完善

#############################################################################################
import maya.cmds as mc
if mc.dockControl('SP2Maya_dockControl',ex = 1):
	mc.deleteUI('SP2Maya_dockControl')
mc.window('SP2Maya',t = 'SP2Maya' )

mc.showWindow()

mainRCL = mc.rowColumnLayout(w = 100,numberOfColumns = 1)
mc.dockControl('SP2Maya_dockControl',area = 'left',content = 'SP2Maya',l = 'SP2Maya' )
mc.separator(style = 'none',h = 20)


#define which renderer is using 

rendererUsing = 'vray'

def connectUVNodeToTextureNode(UVnode,textureNode):
	mc.connectAttr(UVnode +'.outUV',textureNode + '.uvCoord',force = 1)
	mc.connectAttr(UVnode +'.outUvFilterSize',textureNode + '.uvFilterSize',force = 1)
	mc.connectAttr(UVnode +'.coverage',textureNode + '.coverage',force = 1)
	mc.connectAttr(UVnode +'.translateFrame',textureNode + '.translateFrame',force = 1)
	mc.connectAttr(UVnode +'.rotateFrame',textureNode + '.rotateFrame',force = 1)
	mc.connectAttr(UVnode +'.mirrorU',textureNode + '.mirrorU',force = 1)
	mc.connectAttr(UVnode +'.mirrorV',textureNode + '.mirrorV',force = 1)
	mc.connectAttr(UVnode +'.wrapU',textureNode + '.wrapU',force = 1)
	mc.connectAttr(UVnode +'.wrapV',textureNode + '.wrapV',force = 1)
	mc.connectAttr(UVnode +'.repeatUV',textureNode + '.repeatUV',force = 1)
	mc.connectAttr(UVnode +'.vertexUvOne',textureNode + '.vertexUvOne',force = 1)
	mc.connectAttr(UVnode +'.vertexUvTwo',textureNode + '.vertexUvTwo',force = 1)
	mc.connectAttr(UVnode +'.vertexUvThree',textureNode + '.vertexUvThree',force = 1)
	mc.connectAttr(UVnode +'.vertexCameraOne',textureNode + '.vertexCameraOne',force = 1)
	mc.connectAttr(UVnode +'.noiseUV',textureNode + '.noiseUV',force = 1)
	mc.connectAttr(UVnode +'.offset',textureNode + '.offset',force = 1)
	mc.connectAttr(UVnode +'.rotateUV',textureNode + '.rotateUV',force = 1)

#get all file names will be used in the sourceimages folder or user defined folder
def getFileNames(materialName,userDefinedPath):
	if userDefinedPath == '':
		projectPath = mc.workspace(o =1 ,q =1)
		targetPath = projectPath + r'/' + 'sourceimages/'
	else:
		targetPath = userDefinedPath + '\\'
	
	allFileNames = mc.getFileList(folder = targetPath)
	print allFileNames
	fileNamesUsing = []
	fileExsists = False
	for fileName in allFileNames:
		if materialName in fileName:
			fileNamesUsing.append(fileName)
			fileExsists = True
	if not fileExsists:
		mc.error('没有找到对应贴图，请检查')
	return fileNamesUsing
	
		

#udim bool used to judge weather to use udim
udim = False
def UDIM_on(*argus):
	global udim
	udim = True
def UDIM_off(*argus):
	global udim
	udim = False
def UDIM_judge(fileNode):
	if udim:
		mc.setAttr(fileNode + '.uvTilingMode',3)
		mc.setAttr(fileNode + '.uvTileProxyQuality',4)
		
	
#create a dict which containts all the textures that having the materialName
#the keys of the dict are the texture's name
#the values of the dict are the file nodes which ref to the texture 
def createTexturesUsing(fileNamesUsing,userDefinedPath):
	texturesUsing = {}
	targetFileExist = False
	for fileName in fileNamesUsing:
		try:
			tempFile = mc.shadingNode('file',at = 1,icm = 1)
		except:
			tempFile = mc.shadingNode('file',at = 1)
		texturesUsing[fileName] = tempFile
		if userDefinedPath == '':
			mc.setAttr(tempFile + '.fileTextureName','sourceimages' + '\\' + fileName,type = 'string')
			targetFileExist = True
		else:
			mc.setAttr(tempFile + '.fileTextureName',userDefinedPath + '\\' + fileName,type = 'string')
			targetFileExist = True
	if not targetFileExist:
		mc.error('写错名字了吧小伙子，检查一下')
	return texturesUsing

def createVrayShadingNetwork(materialName,texturesUsing):
	#get current version of maya
	version = mc.about(version = 1)[:4]
	version = int(version)
	#if the version is newer than 2016 ,we can use the colormanagement directly
	if version >= 2016:
		#create vray mtl
		vrayMtl = mc.shadingNode('VRayMtl',asShader = 1,n = materialName)
		mc.setAttr(vrayMtl + '.bumpMapType',1)
		try:
			mc.setAttr(vrayMtl + '.brdfType' , 3)
		except:
			mc.warning('当前版本vray没有ggx_brdf，效果可能不好，请注意')

		#create place2dtexture
		UVnode = mc.shadingNode('place2dTexture',au =1)
		#connect textures to material
		for textureUsing in texturesUsing.keys():
			
			if 'Diffuse' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.diffuseColor',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Reflection' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.reflectionColor',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Roughness' in textureUsing:
				mc.setAttr(texturesUsing[textureUsing] + '.invert',1)
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.reflectionGlossiness',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','sRGB',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Glossiness' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.reflectionGlossiness',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'ior' in textureUsing:
				mc.setAttr(vrayMtl + '.lockFresnelIORToRefractionIOR',0)
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.fresnelIOR',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Normal' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.bumpMap',f = 1)
				mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			
	else:
		#create vray mtl
		vrayMtl = mc.shadingNode('VRayMtl',asShader = 1,n = materialName)
		mc.setAttr(vrayMtl + '.bumpMapType',1)
		try:
			mc.setAttr(vrayMtl + '.brdfType' , 3)
		except:
			mc.warning('当前版本vray没有ggx_brdf，效果可能不好，请注意')
		#create place2dtexture
		UVnode = mc.shadingNode('place2dTexture',au =1)
		#connect textures to material
		for textureUsing in texturesUsing.keys():
			if 'Diffuse' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.diffuseColor',f = 1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',2)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Reflection' in textureUsing: 
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.reflectionColor',f = 1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',2)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Roughness' in textureUsing:
				mc.setAttr(texturesUsing[textureUsing] + '.invert',1)
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.reflectionGlossiness',f = 1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',0)
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Glossiness' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.reflectionGlossiness',f = 1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',0)
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'ior' in textureUsing:
				mc.setAttr(vrayMtl + '.lockFresnelIORToRefractionIOR',0)
				mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',vrayMtl + '.fresnelIOR',f =1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',0)
				mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			elif 'Normal' in textureUsing:
				mc.connectAttr(texturesUsing[textureUsing] + '.outColor',vrayMtl + '.bumpMap',f = 1)
				mc.vray("addAttributesFromGroup", texturesUsing[textureUsing], "vray_file_gamma", 1)
				mc.setAttr(texturesUsing[textureUsing] + '.vrayFileColorSpace',0)
				connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])

def createArnoldShadingNetwork(materialName,texturesUsing):
	
	#create aistandard mtl
	aiStandard = mc.shadingNode('aiStandard',asShader = 1,n = materialName)
	mc.setAttr(aiStandard + '.Kd',1)
	mc.setAttr(aiStandard + '.Ks',1)
	try:
		mc.setAttr(aiStandard + '.specularDistribution' ,1 )
	except:
		mc.warning('你使用的arnold版本没有ggx_brdf，效果可能不好')
	
	#create place2dtexture
	UVnode = mc.shadingNode('place2dTexture',au =1)
	
	#connect textures to material
	for textureUsing in texturesUsing.keys():
		if 'Diffuse' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',aiStandard + '.color')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Specular' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',aiStandard + '.KsColor')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Roughness' in textureUsing:
			gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
			mc.setAttr(gammaCorret + '.gammaX',2.2)
			mc.setAttr(gammaCorret + '.gammaY',2.2)
			mc.setAttr(gammaCorret + '.gammaZ',2.2)
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
			mc.connectAttr(gammaCorret + '.outValueX',aiStandard + '.specularRoughness')
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'f0' in textureUsing:
			mc.setAttr(aiStandard + '.specularFresnel',1)
			gammaCorret = mc.shadingNode('gammaCorrect',au = 1)
			mc.setAttr(gammaCorret + '.gammaX',2.2)
			mc.setAttr(gammaCorret + '.gammaY',2.2)
			mc.setAttr(gammaCorret + '.gammaZ',2.2)
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',gammaCorret + '.value')
			mc.connectAttr(gammaCorret + '.outValueX',aiStandard + '.Ksn')
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Normal' in textureUsing:
			bumpNode = mc.shadingNode('bump2d',au = 1)
			mc.setAttr(bumpNode + '.bumpInterp', 1)
			mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',bumpNode + '.bumpValue')
			mc.connectAttr(bumpNode + '.outNormal',aiStandard + '.normalCamera')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
			
def createRedshiftShadingNetwork(materialName,texturesUsing):
    #create redshift mtl
	rsMtl = mc.shadingNode('RedshiftMaterial',asShader = 1,n = materialName)
	mc.setAttr(rsMtl + '.refl_brdf',1)
	
	
	
	#create place2dtexture
	UVnode = mc.shadingNode('place2dTexture',au =1)
	
	#connect textures to material
	for textureUsing in texturesUsing.keys():
		if 'Diffuse' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',rsMtl + '.diffuse_color',f = 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Reflection' in textureUsing:
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',rsMtl + '.refl_color')
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'Glossiness' in textureUsing:
			mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
			mc.setAttr(texturesUsing[textureUsing] + '.invert',1)
			mc.connectAttr(texturesUsing[textureUsing] + '.outAlpha',rsMtl + '.refl_roughness')
			
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'f0' in textureUsing:
			mc.setAttr(rsMtl + '.refl_fresnel_mode',1)
			mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',rsMtl + '.refl_reflectivity',f = 1)
			
			mc.setAttr(texturesUsing[textureUsing] + '.alphaIsLuminance', 1)
			connectUVNodeToTextureNode(UVnode,texturesUsing[textureUsing])
		elif 'ior' in textureUsing:
			mc.setAttr(rsMtl + '.refl_fresnel_mode',3)
			multiplyDivide = mc.shadingNode('multiplyDivide',au = 1)
			mc.setAttr(multiplyDivide + '.input1X',1)
			mc.setAttr(multiplyDivide + '.input1Y',1)
			mc.setAttr(multiplyDivide + '.input1Z',1)
			mc.setAttr(multiplyDivide + '.operation',2)
			mc.connectAttr(texturesUsing[textureUsing] + '.outColor',multiplyDivide + '.input2')
			mc.connectAttr(multiplyDivide + '.output.outputX',rsMtl + '.refl_ior')
			mc.setAttr(texturesUsing[textureUsing] + '.colorSpace','Raw',type = 'string')
					
		elif 'Normal' in textureUsing:
			normalNode = mc.shadingNode('RedshiftNormalMap',au = 1)
			if not udim:
				path = mc.getAttr(texturesUsing[textureUsing] + '.fileTextureName')
			else:
				path = mc.getAttr(texturesUsing[textureUsing] + '.fileTextureName')
				path = path.partition('1001')[0] + '<udim>' + path.partition('1001')[2]
			mc.setAttr(normalNode + '.tex0',path,type = 'string')
			mc.connectAttr(normalNode + '.outDisplacementVector',rsMtl + '.bump_input')
			

    			
def changingRenderer(*argus):
    global rendererUsing
    rendererUsing = mc.optionMenuGrp('Renderer',q = 1 ,v = 1)
def openDirectory(*argus):
	returnDirectory = mc.fileDialog2(fm = 3,ff = None,ds = 1)
	if returnDirectory != None:
		returnDirectory = returnDirectory[0]
	else:
		returnDirectory = ''

	mc.textFieldGrp('texutresPath',e = 1, tx = returnDirectory)	
def main(materialName):
	#get all file names in the sourceimages folder
	userDefinedPath = mc.textFieldGrp(userDefinedPathTextField,q = 1, tx = 1)
	targetFileNames = getFileNames(materialName,userDefinedPath)
	textureNamesUsing =[]
	if udim:
		for targetFileName01 in targetFileNames:
			textureRepeated = False
			for textureUsing in textureNamesUsing:
				if targetFileName01[:-9] == textureUsing[:-9]:
					textureRepeated = True
					break
			if textureRepeated:
				continue
			for targetFileName02 in targetFileNames:
				if (not targetFileName01 == targetFileName02) and (targetFileName01[:-9] == targetFileName02[:-9]):
					
					textureNamesUsing.append(targetFileName01)
					break
					
		print textureNamesUsing
	else:
		textureNamesUsing = targetFileNames			

	#get a dict contains all the textures will be used
	texturesUsing = createTexturesUsing(textureNamesUsing,userDefinedPath)
		
	#judge every texture using, whether is a udim texture,if yes,change the settings
	for textureUsing in texturesUsing.values():
		UDIM_judge(textureUsing)
		
	if rendererUsing == 'vray':
		createVrayShadingNetwork(materialName,texturesUsing)
	elif rendererUsing == 'arnold':
		createArnoldShadingNetwork(materialName,texturesUsing)
	elif rendererUsing == 'redshift':
	    createRedshiftShadingNetwork(materialName,texturesUsing)
	else:
		mc.error('请选择一个你要使用的渲染器,please choose a renderer')

#the UI used to choose renderer
renderer = mc.optionMenuGrp('Renderer', l = 'Renderer',cc = changingRenderer)
mc.menuItem('vray')
mc.menuItem('arnold')
mc.menuItem('redshift')




mc.rowColumnLayout(co = (1,'left',141))

mc.separator(h = 50) 
mc.separator(style = 'out') 
mc.checkBox(l = 'udim textures',onc = UDIM_on,ofc = UDIM_off,align = 'right')  

mc.rowColumnLayout(p = mainRCL)
userDefinedPathTextField = mc.textFieldGrp('texutresPath',l = 'TexutresPath')
mc.iconTextButton(style = 'iconOnly',image = 'xgBrowse.png', p = userDefinedPathTextField,c = openDirectory)
materialNameInput = mc.textFieldButtonGrp(l = 'MaterialName',bl = 'excute',bc = 'main(mc.textFieldButtonGrp(materialNameInput,q = 1,text =1 ))')
mc.separator(style = 'none',h = 20)
mc.separator()
mc.text(l = 'sp2m v1.03d',w =230,al = 'right',hyperlink = 1,ww = 1,ann = 'the version of the script')