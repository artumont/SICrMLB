from pydantic import BaseModel

class RGBColor(BaseModel):
    r: int
    g: int
    b: int
    
    @classmethod
    def pixel_to_color(cls, pixel: tuple[int, int, int]) -> "RGBColor":
        r, g, b = pixel
        return cls(r=r, g=g, b=b)

class RGBRange(BaseModel):
    lower: RGBColor
    upper: RGBColor