import math

class LTX23Sigmas:
    """LTX 2.3 Sigma Calculator"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duration": ("INT", {"default": 121, "min": 1, "max": 10000, "step": 1, "display": "number"}),
                "prompt": ("STRING", {"default": "", "display": "string", "multiline": True}),
                "steps": ("INT", {"default": 4, "min": 4, "max": 50, "step": 1, "display": "number"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sigmas",)
    FUNCTION = "calculate_sigmas"
    CATEGORY = "LTX2.3"

    def I(self, v, points):
        prev = points[0]
        if v <= prev[0]: return prev[1]
        for p in points[1:]:
            if v <= p[0]:
                t = (v - prev[0]) / (p[0] - prev[0])
                return prev[1] + (p[1] - prev[1]) * t
            prev = p
        return points[-1][1]

    def S1(self, d):
        points = [
            (121, 0.84), (241, 0.85), (361, 0.90), (481, 0.95), 
            (601, 0.98), (10000, 0.98)
        ]
        return self.I(d, points)

    def S2(self, d):
        points = [
            (121, 0.78), (241, 0.78), (361, 0.85), (481, 0.89), 
            (601, 0.91), (721, 0.91), (841, 0.92), (10000, 0.92)
        ]
        return self.I(d, points)

    def S3(self, d):
        points = [
            (121, 0.735), (961, 0.735), (1081, 0.740), (10000, 0.740)
        ]
        return self.I(d, points)

    def _interp_curve(self, x, xp, yp):
        """Linear interpolation along a curve defined by (xp, yp) pairs."""
        if x <= xp[0]:
            return yp[0]
        if x >= xp[-1]:
            return yp[-1]
        for i in range(1, len(xp)):
            if x <= xp[i]:
                t = (x - xp[i-1]) / (xp[i] - xp[i-1])
                return yp[i-1] + (yp[i] - yp[i-1]) * t
        return yp[-1]

    def calculate_sigmas(self, duration, prompt="", steps=4):
        # Calculate the base sigma values (the original 5 control points)
        s1_base = self.S1(duration)
        s2_base = self.S2(duration)
        s3_base = self.S3(duration)

        # Apply prompt-length offset to s1 and s2
        words = len(prompt.split())
        if words == 0:
            words = 1
        frames_per_word = duration / words
        offset = 0.0
        if frames_per_word > 10:
            offset = min(0.0075, (frames_per_word - 10) * 0.0002)
        s1 = max(s1_base, min(1.0, s1_base + offset))
        s2 = max(s2_base, min(1.0, s2_base + (offset * 0.5)))
        s3 = s3_base  # S3 is kept strictly to the base table for stability

        # The original 5 control points define the curve shape.
        # They sit at normalized positions [0, 0.25, 0.5, 0.75, 1.0].
        control_positions = [0.0, 0.25, 0.50, 0.75, 1.0]
        control_values = [s1, s2, s3, 0.445, 0.000]

        # For the requested number of steps, sample the curve at evenly-spaced points.
        # N steps → N+1 values (the last is always the 0.000 terminal).
        num_values = steps + 1
        sigmas = []
        for i in range(num_values):
            pos = i / steps  # normalized 0.0 → 1.0
            val = self._interp_curve(pos, control_positions, control_values)
            sigmas.append(f"{val:.3f}")

        result = ", ".join(sigmas)
        return (result,)

NODE_CLASS_MAPPINGS = {"LTX23Sigmas": LTX23Sigmas}
NODE_DISPLAY_NAME_MAPPINGS = {"LTX23Sigmas": "LTX 2.3 Sigma Calculator"}
