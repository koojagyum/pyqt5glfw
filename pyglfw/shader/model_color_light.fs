#version 330 core

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 ourColor;
in vec3 fragPos;
in vec3 fragNormal;
out vec4 color;

uniform vec3 viewPos;
uniform DirLight dirLight;

vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir);

void main()
{
    // vec3 norm = normalize(fragNormal);
    vec3 norm = fragNormal;
    vec3 viewDir = normalize(viewPos - fragPos);

    vec3 result = calcDirLight(dirLight, norm, viewDir);

    color = vec4(result, 1.0);
}

vec3 calcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);
    // Diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // Specular shading
    // vec3 reflectDir = reflect(-lightDir, normal);
    // float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // Combine results
    // vec3 ambient = light.ambient * vec3(texture(material.diffuse, TexCoords));
    // vec3 diffuse = light.diffuse * diff * vec3(texture(material.diffuse, TexCoords));
    // vec3 specular = light.specular * spec * vec3(texture(material.specular, TexCoords));
    // return (ambient + diffuse + specular);

    // temp
    vec3 diffuse = light.diffuse * diff * ourColor;
    return diffuse;
    // return ourColor;
    // return viewDir;
    // return normal;
}
