#version 330 core

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

in vec2 TexCoords;
out vec4 color;

uniform Material material;

void main()
{
    color = texture(material.diffuse, TexCoords);
}
