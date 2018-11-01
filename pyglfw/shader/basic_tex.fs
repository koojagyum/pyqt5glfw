#version 330 core

in vec2 TexCoord;
out vec4 color;

uniform sampler2D input_texture;

void main()
{
  color = texture(input_texture, TexCoord);
}
