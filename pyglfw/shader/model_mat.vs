#version 330 core

layout (location = 0) in vec4 position;
layout (location = 1) in vec2 texcoords;
layout (location = 2) in vec3 normal;

out vec2 TexCoords;
out vec3 FragPos;
out vec3 FragNormal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * position;
    TexCoords = texcoords;
    FragPos = vec3(model * position);
    FragNormal = mat3(transpose(inverse(model))) * normal;
}
