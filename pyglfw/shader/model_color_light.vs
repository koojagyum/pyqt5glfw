#version 330 core

layout (location = 0) in vec4 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normal;

out vec3 ourColor;
out vec3 fragPos;
out vec3 fragNormal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main()
{
    gl_Position = projection * view * model * position;
    ourColor = color;
    fragPos = vec3(model * position);
    fragNormal = mat3(transpose(inverse(model))) * normal;
}
