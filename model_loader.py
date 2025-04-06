import os
import yaml
import torch
import logging
from pathlib import Path

# 创建一个包装类，它使用Model但保持与CustomModel相同的接口
class CustomModelWrapper:
    def __init__(self, model):
        self.model = model
        
    def __call__(self, x):
        # 创建一个虚拟的text张量
        batch_size = x.size(0)
        text = torch.zeros(batch_size, 1, dtype=torch.long, device=x.device)
        
        # 调用Model的forward方法
        return self.model(x, text)

class CustomModelLoader:
    def __init__(self, model_dir='./models'):
        self.model_dir = Path(model_dir)
        self.config = self._load_config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
    def _load_config(self):
        """Load model configuration from yaml file"""
        config_path = self.model_dir / 'model_config.yaml'
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def load_model(self):
        """Load the custom model and weights"""
        try:
            # Import your custom model class
            from custom_example import Model  # 使用官方的Model类
            
            # Initialize model
            model = Model(
                input_channel=1,  # 根据custom_config.yaml
                output_channel=256,
                hidden_size=256,
                num_class=self.config['model']['num_classes']
            )
            
            # Load weights
            weights_path = self.model_dir / self.config['model']['weights']
            if not weights_path.exists():
                raise FileNotFoundError(f"Weights file not found: {weights_path}")
                
            # 加载权重并处理'module.'前缀
            state_dict = torch.load(weights_path, map_location=self.device)
            new_state_dict = {}
            for k, v in state_dict.items():
                name = k[7:] if k.startswith('module.') else k  # 移除'module.'前缀
                new_state_dict[name] = v
            
            model.load_state_dict(new_state_dict)
            model = model.to(self.device)
            model.eval()
            
            # 使用包装类包装模型
            self.model = CustomModelWrapper(model)
            logging.info("Custom model loaded successfully")
            return self.model
            
        except Exception as e:
            logging.error(f"Error loading custom model: {str(e)}")
            raise
            
    def preprocess_image(self, image_path):
        """Preprocess image for model input"""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            import torchvision.transforms as transforms
            
            # 加载自定义配置
            custom_config_path = self.model_dir / self.config['model']['config']
            if custom_config_path.exists():
                with open(custom_config_path, 'r', encoding='utf-8') as f:
                    custom_config = yaml.safe_load(f)
            else:
                custom_config = {'preprocess': {'input_channel': 1, 'normalize_mean': [0.485], 'normalize_std': [0.229]}}
            
            # 获取预处理配置
            input_channel = custom_config.get('preprocess', {}).get('input_channel', 1)
            normalize_mean = custom_config.get('preprocess', {}).get('normalize_mean', [0.485])
            normalize_std = custom_config.get('preprocess', {}).get('normalize_std', [0.229])
            
            # 加载图像
            if input_channel == 1:
                img = Image.open(image_path).convert('L')  # 转换为灰度图
            else:
                img = Image.open(image_path).convert('RGB')  # 转换为RGB
            
            # 调整图像大小以匹配模型的预期输入大小
            img = img.resize((self.config['model']['input_size'][1], self.config['model']['input_size'][0]))
            
            # 转换为张量并归一化
            if input_channel == 1:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize(mean=normalize_mean, std=normalize_std)
                ])
            else:
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize(mean=normalize_mean * 3, std=normalize_std * 3)
                ])
            
            # 添加批次维度
            img_tensor = transform(img).unsqueeze(0)
            
            # 移动到设备
            img_tensor = img_tensor.to(self.device)
            
            return img_tensor
            
        except Exception as e:
            logging.error(f"Error preprocessing image: {str(e)}")
            raise
        
    def postprocess_output(self, output):
        """Postprocess model output"""
        try:
            # 加载自定义配置
            custom_config_path = self.model_dir / self.config['model']['config']
            if custom_config_path.exists():
                with open(custom_config_path, 'r', encoding='utf-8') as f:
                    custom_config = yaml.safe_load(f)
            else:
                custom_config = {'character_list': '0123456789abcdefghijklmnopqrstuvwxyz'}
            
            # 获取字符集
            char_list = custom_config.get('character_list', '0123456789abcdefghijklmnopqrstuvwxyz')
            
            # 获取每个位置的最可能类别
            _, predicted = torch.max(output, 2)
            
            # 转换为字符列表
            result = []
            for i in range(predicted.size(1)):
                char_idx = predicted[0, i].item()
                if char_idx < len(char_list):
                    result.append(char_list[char_idx])
            
            # 移除重复字符和空白字符
            if custom_config.get('postprocess', {}).get('remove_duplicates', False):
                # 简单的重复字符移除
                filtered_result = []
                prev_char = None
                for char in result:
                    if char != prev_char:
                        filtered_result.append(char)
                    prev_char = char
                result = filtered_result
            
            if custom_config.get('postprocess', {}).get('remove_blank', False):
                # 移除空白字符
                result = [char for char in result if char != ' ']
            
            # 将字符连接成字符串
            return ''.join(result)
            
        except Exception as e:
            logging.error(f"Error postprocessing output: {str(e)}")
            raise
        
    def predict(self, image_path):
        """Predict text in the image"""
        try:
            # 确保模型已加载
            if self.model is None:
                self.load_model()
                
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Get model prediction
            with torch.no_grad():
                output = self.model(processed_image)
            
            # Postprocess output
            text_result = self.postprocess_output(output)
            
            # 将结果转换为数组格式
            return [{'text': text_result, 'confidence': 1.0}]  # 添加置信度信息
            
        except Exception as e:
            logging.error(f"Error in prediction: {str(e)}")
            raise 