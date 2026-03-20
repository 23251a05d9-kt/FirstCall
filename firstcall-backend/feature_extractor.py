import cv2
import numpy as np
import os

class VideoFeatureExtractor:
    """Extract powerful features from videos for accident detection"""
    
    def __init__(self, frame_size=(100, 100), max_frames=25):
        self.frame_size = frame_size
        self.max_frames = max_frames
        
    def extract_video_features(self, video_path):
        """Extract comprehensive features from a video"""
        try:
            # Load video frames
            frames = self.load_video(video_path)
            if len(frames) == 0:
                return self.get_default_features()
            
            # Extract multiple types of features
            intensity_features = self.extract_intensity_features(frames)
            texture_features = self.extract_texture_features(frames)
            motion_features = self.extract_motion_features(frames)
            statistical_features = self.extract_statistical_features(frames)
            temporal_features = self.extract_temporal_features(frames)
            
            # Combine all features
            all_features = np.concatenate([
                intensity_features,
                texture_features,
                motion_features,
                statistical_features,
                temporal_features
            ])
            
            return all_features
            
        except Exception as e:
            print(f"Error processing {video_path}: {str(e)[:50]}")
            return self.get_default_features()
    
    def load_video(self, video_path):
        """Load frames from video with .264 support"""
        frames = []
        
        # Try multiple methods for .264 files
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)  # First try FFMPEG
        
        if not cap.isOpened():
            cap = cv2.VideoCapture(video_path)  # Try standard method
        
        if cap.isOpened():
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // self.max_frames) if total_frames > 0 else 1
            
            frame_idx = 0
            while len(frames) < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    # Convert to grayscale and resize
                    if len(frame.shape) == 3:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = frame
                    
                    gray = cv2.resize(gray, self.frame_size)
                    frames.append(gray)
                
                frame_idx += 1
                if frame_idx > 1000:  # Safety limit
                    break
            
            cap.release()
        
        return frames
    
    def extract_intensity_features(self, frames):
        """Extract brightness/contrast features"""
        features = []
        
        for frame in frames:
            features.extend([
                np.mean(frame),           # Average brightness
                np.std(frame),            # Contrast
                np.max(frame),            # Maximum brightness
                np.min(frame),            # Minimum brightness
                np.median(frame),         # Median brightness
                np.percentile(frame, 25), # 25th percentile
                np.percentile(frame, 75), # 75th percentile
            ])
        
        # Take mean across frames
        features = np.array(features).reshape(len(frames), -1)
        return np.mean(features, axis=0)
    
    def extract_texture_features(self, frames):
        """Extract texture features using gradients"""
        features = []
        
        for frame in frames:
            # Sobel gradients
            sobelx = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
            
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            gradient_orientation = np.arctan2(np.abs(sobely), np.abs(sobelx))
            
            features.extend([
                np.mean(gradient_magnitude),    # Average edge strength
                np.std(gradient_magnitude),     # Edge variation
                np.mean(gradient_orientation),  # Average edge direction
            ])
        
        features = np.array(features).reshape(len(frames), -1)
        return np.mean(features, axis=0)
    
    def extract_motion_features(self, frames):
        """Extract motion features from consecutive frames"""
        if len(frames) < 2:
            return np.zeros(5)
        
        motion_values = []
        for i in range(1, len(frames)):
            # Frame difference as motion approximation
            diff = cv2.absdiff(frames[i], frames[i-1])
            motion_values.append(np.mean(diff))
        
        motion_values = np.array(motion_values)
        
        return np.array([
            np.mean(motion_values),      # Average motion
            np.std(motion_values),       # Motion variation
            np.max(motion_values),       # Maximum motion
            np.min(motion_values),       # Minimum motion
            np.percentile(motion_values, 90)  # 90th percentile
        ])
    
    def extract_statistical_features(self, frames):
        """Extract statistical features"""
        if len(frames) == 0:
            return np.zeros(4)
        
        all_pixels = np.concatenate([frame.flatten() for frame in frames])
        
        return np.array([
            np.mean(all_pixels),        # Global mean
            np.std(all_pixels),         # Global std
            np.var(all_pixels),         # Variance
            np.median(all_pixels),      # Global median
        ])
    
    def extract_temporal_features(self, frames):
        """Extract temporal pattern features"""
        if len(frames) < 3:
            return np.zeros(3)
        
        # Mean intensity over time
        intensity_over_time = [np.mean(frame) for frame in frames]
        
        # Rate of change
        diffs = np.diff(intensity_over_time)
        
        return np.array([
            np.mean(diffs),            # Average rate of change
            np.std(diffs),             # Variability of change
            np.max(np.abs(diffs)),     # Maximum sudden change
        ])
    
    def get_default_features(self):
        """Return default features if video can't be processed"""
        # Total features = 7(intensity) + 3(texture) + 5(motion) + 4(statistical) + 3(temporal) = 22
        return np.zeros(22)