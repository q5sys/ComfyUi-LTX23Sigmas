import math

class LTX23Sigmas:
    """LTX 2.3 Sigma Calculator"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duration": ("INT", {"default": 121, "min": 1, "max": 10000, "step": 1, "display": "number"}),
                "prompt": ("STRING", {"default": "", "display": "string", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sigmas",)
    FUNCTION = "calculate_sigmas"
    CATEGORY = "LTX2.3"

    def I(self, v, points):
        prev = points[0]
        for p in points[1:]:
            if v <= p[0]:
                if v == prev[0]: return prev[1]
                if v == p[0]: return p[1]
                t = (v - prev[0]) / (p[0] - prev[0])
                return prev[1] + (p[1] - prev[1]) * t
            prev = p
        return points[-1][1]

    def S1(self, d):
        points = [(121, 0.84), (241, 0.85), (361, 0.92), (481, 0.95), (10000, 0.98)]
        return self.I(d, points)

    def S2(self, d):
        points = [(121, 0.78), (241, 0.78), (361, 0.85), (481, 0.89), (10000, 0.93)]
        return self.I(d, points)

    def S3(self, d):
        points = [(121, 0.735), (1441, 0.745), (10000, 0.745)]
        return self.I(d, points)

    def calculate_sigmas(self, duration, prompt=""):
        s1 = self.S1(duration)
        s2 = self.S2(duration)
        s3 = self.S3(duration)
        words = len(prompt.split())
        if words == 0: words = 1
        frames_per_word = duration / words
        offset = 0.0
        if frames_per_word > 10:
            offset = min(0.0075, (frames_per_word - 10) * 0.0002)
        s1 = min(1.0, s1 + offset)
        s2 = min(1.0, s2 + (offset * 0.5)) 
        result = f"{s1:.3f}, {s2:.3f}, {s3:.3f}, 0.445, 0.000"
        return (result,)

NODE_CLASS_MAPPINGS = {"LTX23Sigmas": LTX23Sigmas}
NODE_DISPLAY_NAME_MAPPINGS = {"LTX23Sigmas": "LTX 2.3 Sigma Calculator"}