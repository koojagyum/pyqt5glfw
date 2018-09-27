#version 330 core

in vec2 TexCoord;
out vec4 color;

uniform sampler2D inputTexture;
uniform int useUniformColor;

void main()
{
  color = texture(inputTexture, TexCoord);
}
